# app/api/routes/lab_results.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.lab_result import LabStudy, LabResult
from app.schemas.lab_result import (
    LabStudyCreate,
    LabStudyResponse,
    LabStudyUpdate,
    LabResultBase,
    LabResultResponse,
    LabResultUpdate,
    ParameterEvolutionResponse,
    ParameterDataPoint
)

router = APIRouter(
    prefix="/lab-studies",
    tags=["Lab Studies"]
)


# Crear estudio con sus resultados
@router.post("/", response_model=LabStudyResponse)
def create_lab_study(
    data: LabStudyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_study = LabStudy(
        id_user=current_user.id_user,
        laboratory_name=data.laboratory_name,
        test_date=data.test_date
    )
    db.add(new_study)
    db.flush()  # obtener id_study antes del commit

    for res_data in data.results:
        db.add(LabResult(
            **res_data.model_dump(),
            id_study=new_study.id_study
        ))

    try:
        db.commit()
        db.refresh(new_study)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al guardar el estudio")

    return new_study


# Obtener todos mis estudios
@router.get("/me", response_model=List[LabStudyResponse])
def get_my_studies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(LabStudy)
        .filter(LabStudy.id_user == current_user.id_user)
        .order_by(LabStudy.test_date.desc())
        .all()
    )


# Obtener un estudio por id
@router.get("/me/{id_study}", response_model=LabStudyResponse)
def get_my_study(
    id_study: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    study = (
        db.query(LabStudy)
        .filter(
            LabStudy.id_study == id_study,
            LabStudy.id_user == current_user.id_user
        )
        .first()
    )
    if not study:
        raise HTTPException(status_code=404, detail="Estudio no encontrado")
    return study


# Evolución longitudinal de un parámetro específico
# Ej: GET /lab-studies/me/evolution/TSH
@router.get("/me/evolution/{parameter}", response_model=ParameterEvolutionResponse)
def get_parameter_evolution(
    parameter: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    results = (
        db.query(LabResult, LabStudy)
        .join(LabStudy, LabResult.id_study == LabStudy.id_study)
        .filter(
            LabStudy.id_user == current_user.id_user,
            LabResult.parameter.ilike(parameter)  # case-insensitive
        )
        .order_by(LabStudy.test_date.asc())
        .all()
    )

    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontraron resultados para el parámetro '{parameter}'"
        )

    data_points = [
        ParameterDataPoint(
            test_date=study.test_date,
            value=result.value,
            unit=result.unit,
            reference_range=result.reference_range,
            laboratory_name=study.laboratory_name,
            id_study=study.id_study
        )
        for result, study in results
    ]

    return ParameterEvolutionResponse(
        parameter=parameter,
        data_points=data_points
    )



# Eliminar un estudio (elimina también sus resultados por cascade)
@router.delete("/me/{id_study}")
def delete_my_study(
    id_study: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    study = (
        db.query(LabStudy)
        .filter(
            LabStudy.id_study == id_study,
            LabStudy.id_user == current_user.id_user
        )
        .first()
    )
    if not study:
        raise HTTPException(status_code=404, detail="Estudio no encontrado")

    db.delete(study)
    db.commit()
    return {"detail": "Estudio eliminado correctamente"}

@router.patch("/me/{id_study}", response_model=LabStudyResponse)
def update_my_study(
    id_study: int,
    data: LabStudyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    study = db.query(LabStudy).filter(
        LabStudy.id_study == id_study,
        LabStudy.id_user == current_user.id_user
    ).first()
    if not study:
        raise HTTPException(status_code=404, detail="Estudio no encontrado")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(study, key, value)

    db.commit()
    db.refresh(study)
    return study


@router.patch("/me/{id_study}/results/{id_result}", response_model=LabResultResponse)
def update_my_result(
    id_study: int,
    id_result: int,
    data: LabResultUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verificar que el estudio pertenece a la usuaria
    study = db.query(LabStudy).filter(
        LabStudy.id_study == id_study,
        LabStudy.id_user == current_user.id_user
    ).first()
    if not study:
        raise HTTPException(status_code=404, detail="Estudio no encontrado")

    result = db.query(LabResult).filter(
        LabResult.id_result == id_result,
        LabResult.id_study == id_study
    ).first()
    if not result:
        raise HTTPException(status_code=404, detail="Resultado no encontrado")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(result, key, value)

    db.commit()
    db.refresh(result)
    return result


@router.post("/me/{id_study}/results", response_model=LabResultResponse)
def add_result_to_study(
    id_study: int,
    data: LabResultBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    study = db.query(LabStudy).filter(
        LabStudy.id_study == id_study,
        LabStudy.id_user == current_user.id_user
    ).first()
    if not study:
        raise HTTPException(status_code=404, detail="Estudio no encontrado")

    result = LabResult(**data.model_dump(), id_study=id_study)
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


@router.delete("/me/{id_study}/results/{id_result}")
def delete_my_result(
    id_study: int,
    id_result: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    study = db.query(LabStudy).filter(
        LabStudy.id_study == id_study,
        LabStudy.id_user == current_user.id_user
    ).first()
    if not study:
        raise HTTPException(status_code=404, detail="Estudio no encontrado")

    result = db.query(LabResult).filter(
        LabResult.id_result == id_result,
        LabResult.id_study == id_study
    ).first()
    if not result:
        raise HTTPException(status_code=404, detail="Resultado no encontrado")

    db.delete(result)
    db.commit()
    return {"detail": "Resultado eliminado correctamente"}