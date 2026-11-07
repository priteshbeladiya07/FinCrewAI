from fastapi import APIRouter, HTTPException, status

from app.schemas.stock_schema import StockQuoteResponse
from app.services.stock_service import get_stock_quote

from app.utils.logger import get_logger


router = APIRouter()

logger = get_logger(__name__)


@router.get(
    "/{symbol}/quote",
    response_model=StockQuoteResponse
)
def stock_quote(symbol: str):

    try:

        return get_stock_quote(symbol)

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error)
        )

    except LookupError as error:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )

    except Exception:

        logger.exception(
            "Stock quote API failed for %s",
            symbol
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to retrieve stock data from the market-data provider."
        )