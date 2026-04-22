from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.services.pdf.utils.formatters import format_date, format_date_pdf
from app.services.chart_service import generate_cycle_charts
from app.services.pdf_service import generate_cycle_report_pdf, generate_full_clinical_pdf
from app.services.report_data_service import get_full_clinical_report, get_cycle_report_by_id

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

    charts = generate_cycle_charts(data["last_cycle"])

    pdf_path = generate_full_clinical_pdf(data, charts)

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename="historial_clinico.pdf"
    )

@router.get("/cycle-report/{cycle_id}")
def download_cycle_report(
    cycle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    data = get_cycle_report_by_id(db, current_user, cycle_id)

    if not data:
        raise HTTPException(status_code=404, detail="Cycle not found")

    charts = generate_cycle_charts(data["cycle"])

    pdf_path = generate_cycle_report_pdf(data, charts)

    start_date = format_date_pdf(data["cycle"].start_date)
    if data["cycle"].end_date:
        end_date = format_date_pdf(data["cycle"].end_date)
    else:
        end_date = format_date_pdf(datetime.now().date())

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f'ciclo_{start_date}_{end_date}.pdf'
    )
