from sqlalchemy.orm import Session
from app.models.cycle import Cycle
from app.models.clinical_history import ClinicalHistory

from datetime import timedelta

def _compute_cycle_lengths(cycles: list) -> list[int]:
    """Calcula las longitudes en días entre start_dates consecutivos."""
    start_dates = sorted(
        [c.start_date for c in cycles if c.start_date is not None]
    )
    if len(start_dates) < 2:
        return []
    return [
        (start_dates[i] - start_dates[i - 1]).days
        for i in range(1, len(start_dates))
    ]


def compute_regularity(cycle_lengths: list[int]) -> str:
    """
    Determina regularidad:
    - Irregular si algún ciclo es <21 o >35 días
    - Irregular si la variación entre ciclos consecutivos es >=7 días en algún par
    - Regular en cualquier otro caso
    """
    if not cycle_lengths:
        return "regular"

    for length in cycle_lengths:
        if length < 21 or length > 35:
            return "irregular"

    for i in range(1, len(cycle_lengths)):
        if abs(cycle_lengths[i] - cycle_lengths[i - 1]) >= 7:
            return "irregular"

    return "regular"


def update_cycle_stats(db: Session, id_history: int) -> None:
    """
    Recalcula y persiste en ClinicalHistory:
    - average_menstrual_cycle
    - average_ovulation
    - last_period_date
    - regularity
    Debe llamarse cada vez que se crea o cierra un ciclo.
    """
    history = db.query(ClinicalHistory).filter(
        ClinicalHistory.id_history == id_history
    ).first()
    if not history:
        return

    cycles = (
        db.query(Cycle)
        .filter(Cycle.id_history == id_history)
        .order_by(Cycle.start_date)
        .all()
    )

    cycle_lengths = _compute_cycle_lengths(cycles)

    if cycle_lengths:
        avg = round(sum(cycle_lengths) / len(cycle_lengths))
        history.average_menstrual_cycle = avg
        history.average_ovulation = avg // 2
        history.regularity = compute_regularity(cycle_lengths)
    
    # Fecha de última menstruación: start_date del ciclo más reciente
    cycles_with_date = [c for c in cycles if c.start_date is not None]
    if cycles_with_date:
        history.last_period_date = max(
            cycles_with_date, key=lambda c: c.start_date
        ).start_date

    db.commit()


def recalculate_cycle_end_dates(db: Session, id_history: int) -> None:
    """
    Recalcula end_date de todos los ciclos de una historia
    ordenándolos por start_date. Cada ciclo termina el día
    anterior al inicio del siguiente.
    """
    cycles = (
        db.query(Cycle)
        .filter(Cycle.id_history == id_history)
        .order_by(Cycle.start_date.asc())
        .all()
    )
    for i, cycle in enumerate(cycles):
        if i < len(cycles) - 1:
            cycle.end_date = cycles[i + 1].start_date - timedelta(days=1)
        else:
            cycle.end_date = None  # El más reciente queda abierto
    db.commit()