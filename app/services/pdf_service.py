from app.services.pdf.builders.full_clinical_report_builder import build_full_clinical_report_pdf
from app.assets.fonts_config import register_fonts


def generate_full_clinical_pdf(data, charts):
    register_fonts()
    return build_full_clinical_report_pdf(data, charts)