"""CSV import/export endpoints for holdings."""

import csv
import io
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.domain.db_models import Holding

router = APIRouter(prefix='/csv', tags=['csv'])


@router.get('/holdings')
async def export_holdings(
    session: AsyncSession = Depends(get_session),
) -> Any:
    """Export holdings as CSV."""
    result = await session.execute(select(Holding))
    holdings = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['symbol', 'quantity', 'average_cost', 'notes'])

    for h in holdings:
        writer.writerow([h.symbol, h.quantity, h.average_cost, h.notes])

    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename=holdings.csv'},
    )


@router.post('/holdings/import')
async def import_holdings(
    file: UploadFile,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Import holdings from CSV file."""
    if not file.filename or not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail='Only CSV files accepted')

    content = await file.read()
    text = content.decode('utf-8')
    reader = csv.DictReader(io.StringIO(text))

    imported = 0
    errors = 0

    for row in reader:
        try:
            symbol = row.get('symbol', '').strip().upper()
            quantity = float(row.get('quantity', 0))
            avg_cost = float(row.get('average_cost', 0))
            notes = row.get('notes', '')

            if not symbol or quantity <= 0:
                errors += 1
                continue

            holding = Holding(
                symbol=symbol,
                quantity=quantity,
                average_cost=avg_cost,
                notes=notes,
            )
            session.add(holding)
            imported += 1
        except (ValueError, KeyError):
            errors += 1
            continue

    await session.commit()
    return {'imported': imported, 'errors': errors}
