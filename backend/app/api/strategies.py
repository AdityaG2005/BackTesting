from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.nlp_strategy import generate_strategy_code, validate_syntax, compile_strategy_class
from app.core.bias_check import check_lookahead_bias
from app.db.session import SessionLocal
from app.models import Instrument, Bar

router = APIRouter()

AVAILABLE_STRATEGIES = [
    {
        "id": "moving_average_crossover",
        "name": "Moving Average Crossover",
        "description": "Buys when a short-term moving average crosses above a long-term moving average, sells on the reverse.",
        "parameters": [
            {"name": "short_window", "type": "int", "default": 20},
            {"name": "long_window", "type": "int", "default": 50},
        ],
    },
    {
        "id": "rsi_mean_reversion",
        "name": "RSI Mean Reversion",
        "description": "Buys when RSI is oversold, sells when RSI is overbought, betting on reversion to the mean.",
        "parameters": [
            {"name": "period", "type": "int", "default": 14},
            {"name": "oversold", "type": "int", "default": 30},
            {"name": "overbought", "type": "int", "default": 70},
        ],
    },
]


@router.get("/strategies")
def list_strategies():
    return {"strategies": AVAILABLE_STRATEGIES}


class StrategyDescriptionRequest(BaseModel):
    description: str
    validation_ticker: str = "AAPL"


@router.post("/strategies/from-description")
def generate_strategy_from_description(request: StrategyDescriptionRequest):
    code = generate_strategy_code(request.description)

    is_valid, syntax_error = validate_syntax(code)
    if not is_valid:
        raise HTTPException(
            status_code=422,
            detail=f"Generated code failed syntax validation: {syntax_error}"
        )

    try:
        strategy_class = compile_strategy_class(code)
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Generated code failed to compile: {str(e)}"
        )

    session = SessionLocal()
    try:
        instrument = session.query(Instrument).filter_by(ticker=request.validation_ticker).first()
        if instrument is None:
            raise HTTPException(status_code=400, detail=f"No data available for {request.validation_ticker}")

        bars = (
            session.query(Bar)
            .filter_by(instrument_id=instrument.id)
            .order_by(Bar.timestamp)
            .all()
        )

        bias_result = check_lookahead_bias(
            strategy_factory=lambda: strategy_class(),
            bars=bars,
            ticker=request.validation_ticker
        )

        if not bias_result["passed"]:
            raise HTTPException(
                status_code=422,
                detail=f"Generated strategy failed lookahead-bias check: {bias_result['mismatches']}"
            )

        return {
            "accepted": True,
            "code": code,
            "bias_check": bias_result
        }
    finally:
        session.close()