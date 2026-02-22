import io
from datetime import date

import pandas as pd
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, g, send_file,
)

from app import db
from app.models import PurchaseRequisition, Comment
from app.auth import buyer_required
from app.notifications import send_notification

buyer_bp = Blueprint('buyer', __name__)

VALID_STATUSES = ['Pending', 'In Review', 'Approved', 'Rejected', 'Completed', 'Cancelled']


def _apply_filters(query, args):
    """Apply search/status/date filters from request args or form data."""
    status = args.get('status', '')
    search = args.get('search', '').strip()
    date_from = args.get('date_from', '')
    date_to = args.get('date_to', '')

    if status and status in VALID_STATUSES:
        query = query.filter_by(status=status)

    if search:
        like = f'%{search}%'
        query = query.filter(
            db.or_(
                PurchaseRequisition.title.ilike(like),
                PurchaseRequisition.pr_number.ilike(like),
                PurchaseRequisition.requester_email.ilike(like),
                PurchaseRequisition.vendor.ilike(like),
            )
        )

    if date_from:
        try:
            query = query.filter(PurchaseRequisition.request_date >= date.fromisoformat(date_from))
        except ValueError:
            pass

    if date_to:
        try:
            d = date.fromisoformat(date_to)
            query = query.filter(PurchaseRequisition.request_date < date(d.year, d.month, d.day + 1) if d.day < 28
                                 else PurchaseRequisition.request_date <= d)
        except (ValueError, OverflowError):
            pass

    return query


# ── Dashboard ──────────────────────────────────────────────────────

@buyer_bp.route('/dashboard')
@buyer_required
def dashboard():
    query = _apply_filters(PurchaseRequisition.query, request.args)
    prs = query.order_by(PurchaseRequisition.request_date.desc()).all()

    return render_template(
        'buyer/dashboard.html',
        prs=prs,
        statuses=VALID_STATUSES,
        filters={
            'status': request.args.get('status', ''),
            'search': request.args.get('search', ''),
            'date_from': request.args.get('date_from', ''),
            'date_to': request.args.get('date_to', ''),
        },
    )


# ── Status Change ──────────────────────────────────────────────────

@buyer_bp.route('/pr/<int:pr_id>/status', methods=['POST'])
@buyer_required
def update_status(pr_id):
    pr = PurchaseRequisition.query.get_or_404(pr_id)
    new_status = request.form.get('status', '')

    if new_status not in VALID_STATUSES:
        flash('Invalid status.', 'error')
        return redirect(url_for('requester.view_pr', pr_id=pr.id))

    old_status = pr.status
    pr.status = new_status
    db.session.commit()

    send_notification(pr.requester_email, pr.pr_number, new_status)
    flash(f'Status updated from "{old_status}" to "{new_status}".', 'success')
    return redirect(url_for('requester.view_pr', pr_id=pr.id))


# ── Comments ───────────────────────────────────────────────────────

@buyer_bp.route('/pr/<int:pr_id>/comment', methods=['POST'])
@buyer_required
def add_comment(pr_id):
    pr = PurchaseRequisition.query.get_or_404(pr_id)
    body = request.form.get('body', '').strip()

    if not body:
        flash('Comment cannot be empty.', 'error')
        return redirect(url_for('requester.view_pr', pr_id=pr.id))

    comment = Comment(
        requisition_id=pr.id,
        author_email=g.current_user_email,
        body=body,
    )
    db.session.add(comment)
    db.session.commit()

    flash('Comment added.', 'success')
    return redirect(url_for('requester.view_pr', pr_id=pr.id))


# ── Export ─────────────────────────────────────────────────────────

@buyer_bp.route('/export')
@buyer_required
def export_page():
    return render_template('buyer/export.html', statuses=VALID_STATUSES)


@buyer_bp.route('/export/download', methods=['POST'])
@buyer_required
def export_download():
    query = _apply_filters(PurchaseRequisition.query, request.form)
    prs = query.order_by(PurchaseRequisition.request_date.desc()).all()
    fmt = request.form.get('format', 'xlsx')

    if not prs:
        flash('No requisitions match the selected filters.', 'error')
        return redirect(url_for('buyer.export_page'))

    headers_data = []
    items_data = []
    for pr in prs:
        headers_data.append({
            'PR Number': pr.pr_number,
            'Title': pr.title,
            'Requester': pr.requester_email,
            'Request Date': pr.request_date.strftime('%Y-%m-%d %H:%M'),
            'Need By': pr.need_by_date.strftime('%Y-%m-%d'),
            'Type': pr.purchase_type,
            'Cost Code': pr.cost_code,
            'EA Number': pr.ea_number or '',
            'Vendor': pr.vendor or '',
            'Status': pr.status,
            'Outage': 'Yes' if pr.is_outage else 'No',
            'Emergency': 'Yes' if pr.is_emergency else 'No',
            'Quote Attached': 'Yes' if pr.is_quote_attached else 'No',
            'Manager Approved': 'Yes' if pr.manager_approval_received else 'No',
        })
        for item in pr.items:
            items_data.append({
                'PR Number': pr.pr_number,
                'Quantity': item.quantity,
                'Description': item.description,
                'Part Number': item.part_number or '',
                'Unit Price': item.price,
                'Subtotal': item.quantity * item.price,
            })

    buf = io.BytesIO()

    if fmt == 'csv':
        pd.DataFrame(headers_data).to_csv(buf, index=False)
        buf.seek(0)
        return send_file(
            buf, mimetype='text/csv',
            as_attachment=True, download_name='requisitions.csv',
        )

    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        pd.DataFrame(headers_data).to_excel(writer, sheet_name='Requisitions', index=False)
        if items_data:
            pd.DataFrame(items_data).to_excel(writer, sheet_name='Line Items', index=False)
    buf.seek(0)
    return send_file(
        buf,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True, download_name='requisitions.xlsx',
    )
