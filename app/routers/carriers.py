from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from app.database import get_db

router = APIRouter()


@router.get("/carriers")
def list_carriers(
    persona: Optional[str] = Query(default=None, description="Filter by persona"),
    search: Optional[str] = Query(default=None, description="Search by legal_name"),
    limit: int = Query(default=100, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List carriers with joined census + intelligence data.
    Sorted by score DESC.
    """
    try:
        # Build WHERE clauses
        conditions = []
        params = {"limit": limit, "offset": offset}

        if persona:
            conditions.append("ci.persona = :persona")
            params["persona"] = persona

        if search:
            conditions.append("c.legal_name ILIKE :search")
            params["search"] = f"%{search}%"

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        query = f"""
            SELECT
                c.dot_number,
                c.legal_name,
                c.phy_city,
                c.phy_state,
                c.power_units,
                c.hm_ind,
                c.safety_rating,
                ci.coverage_max,
                ci.n_insurers,
                ci.switch_rate,
                ci.persona,
                ci.est_renewal_days,
                ci.score
            FROM fmcsa.census_full c
            LEFT JOIN fmcsa.carrier_intelligence ci ON c.dot_number = ci.dot_number
            {where_clause}
            ORDER BY ci.score DESC NULLS LAST
            LIMIT :limit OFFSET :offset
        """

        result = db.execute(text(query), params)
        rows = [dict(row._mapping) for row in result]

        # Get total count
        count_query = f"""
            SELECT COUNT(*)
            FROM fmcsa.census_full c
            LEFT JOIN fmcsa.carrier_intelligence ci ON c.dot_number = ci.dot_number
            {where_clause}
        """
        count_params = {k: v for k, v in params.items() if k not in ["limit", "offset"]}
        total = db.execute(text(count_query), count_params).scalar()

        return {
            "data": rows,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": total
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/carriers/{dot_number}")
def get_carrier(dot_number: str, db: Session = Depends(get_db)):
    """
    Get full carrier detail: census + intelligence + insurance history.
    Handles DOT number padding for insurance_history join.
    """
    try:
        # Get census + intelligence data
        census_query = """
            SELECT c.*,
                   ci.coverage_max,
                   ci.n_insurers,
                   ci.switch_rate,
                   ci.persona,
                   ci.est_renewal_days,
                   ci.score
            FROM fmcsa.census_full c
            LEFT JOIN fmcsa.carrier_intelligence ci ON c.dot_number = ci.dot_number
            WHERE c.dot_number = :dot_number
        """
        result = db.execute(text(census_query), {"dot_number": dot_number})
        carrier = result.fetchone()

        if not carrier:
            raise HTTPException(status_code=404, detail=f"Carrier with DOT {dot_number} not found")

        carrier_data = dict(carrier._mapping)

        # Get insurance history (DOT padded to 8 digits)
        padded_dot = dot_number.zfill(8)
        insurance_query = """
            SELECT *
            FROM fmcsa.insurance_history
            WHERE dot_number = :padded_dot
            ORDER BY eff_date DESC
        """
        insurance_result = db.execute(text(insurance_query), {"padded_dot": padded_dot})
        insurance_history = [dict(row._mapping) for row in insurance_result]

        return {
            "carrier": carrier_data,
            "insurance_history": insurance_history
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
