from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.services.chart_service import stress_chart
from app.services.pdf_service import generate_full_clinical_pdf
from app.services.report_data_service import get_full_clinical_report

router = APIRouter(
    prefix="/reports",
    tags=["reports"]
)

@router.get("/full-report")
def download_full_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    data = get_full_clinical_report(db, current_user)

    chart = stress_chart(data["cycles"])

    pdf_path = generate_full_clinical_pdf(data, chart)

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename="clinical_report.pdf"
    )