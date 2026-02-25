import io
import os
import re
from datetime import date

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, g, abort, send_file,
)

from app import db
from app.models import PurchaseRequisition, RequisitionItem, Attachment

requester_bp = Blueprint('requester', __name__)

COST_CODE_REGEX = re.compile(r'^\d{5}-\d{6}$')
VALID_PURCHASE_TYPES = {'Service', 'Material', 'Service-Material'}
ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png'}
MAX_TOTAL_UPLOAD = 2 * 1024 * 1024  # 2MB


def _parse_items(form):
    """Extract item rows from form data, tolerating index gaps from deleted rows."""
    indices = sorted(set(
        int(key.split('-')[1])
        for key in form
        if key.startswith('items-') and key.endswith('-quantity')
    ))
    items = []
    errors = []
    for idx in indices:
        row = len(items) + 1
        qty_str = form.get(f'items-{idx}-quantity', '').strip()
        desc = form.get(f'items-{idx}-description', '').strip()
        part = form.get(f'items-{idx}-part_number', '').strip() or None
        price_str = form.get(f'items-{idx}-price', '').strip()

        qty = None
        price = None

        if not qty_str:
            errors.append(f'Item {row}: Quantity is required.')
        else:
            try:
                qty = int(qty_str)
                if qty <= 0:
                    errors.append(f'Item {row}: Quantity must be positive.')
            except ValueError:
                errors.append(f'Item {row}: Quantity must be a whole number.')

        if not desc:
            errors.append(f'Item {row}: Description is required.')

        if price_str:
            try:
                price = float(price_str)
                if price < 0:
                    errors.append(f'Item {row}: Price cannot be negative.')
            except ValueError:
                errors.append(f'Item {row}: Price must be a number.')

        items.append({
            'quantity': qty,
            'description': desc,
            'part_number': part,
            'price': price,
        })

    return items, errors


def _build_form_data(form, items):
    """Re-pack form values for template re-rendering on validation failure."""
    return {
        'title': form.get('title', ''),
        'need_by_date': form.get('need_by_date', ''),
        'purchase_type': form.get('purchase_type', ''),
        'cost_code': form.get('cost_code', ''),
        'ea_number': form.get('ea_number', ''),
        'vendor': form.get('vendor', ''),
        'is_outage': form.get('is_outage') == 'on',
        'is_emergency': form.get('is_emergency') == 'on',
        'is_quote_attached': form.get('is_quote_attached') == 'on',
        'manager_approval_received': form.get('manager_approval_received') == 'on',
        'items': items,
    }


@requester_bp.route('/new', methods=['GET', 'POST'])
def new_pr():
    if request.method == 'GET':
        return render_template('requester/new_pr.html', form={})

    errors = []

    # --- Header validation ---
    title = request.form.get('title', '').strip()
    if not title:
        errors.append('Title is required.')

    need_by_date_str = request.form.get('need_by_date', '')
    need_by_date = None
    if not need_by_date_str:
        errors.append('Need-by date is required.')
    else:
        try:
            need_by_date = date.fromisoformat(need_by_date_str)
            if need_by_date <= date.today():
                errors.append('Need-by date must be in the future.')
        except ValueError:
            errors.append('Invalid need-by date format.')

    purchase_type = request.form.get('purchase_type', '')
    if purchase_type not in VALID_PURCHASE_TYPES:
        errors.append('Please select a valid purchase type.')

    cost_code = request.form.get('cost_code', '').strip()
    if not cost_code:
        errors.append('Cost code is required.')
    elif not COST_CODE_REGEX.match(cost_code):
        errors.append('Cost code must match #####-###### (5 digits, dash, 6 digits).')

    is_outage = request.form.get('is_outage') == 'on'
    is_emergency = request.form.get('is_emergency') == 'on'
    is_quote_attached = request.form.get('is_quote_attached') == 'on'
    manager_approval_received = request.form.get('manager_approval_received') == 'on'
    ea_number = request.form.get('ea_number', '').strip() or None
    vendor = request.form.get('vendor', '').strip() or None

    # --- Items validation ---
    items_data, item_errors = _parse_items(request.form)
    errors.extend(item_errors)
    if not items_data:
        errors.append('At least one item is required.')

    # --- Attachment validation ---
    uploaded_files = request.files.getlist('attachments')
    valid_files = []
    total_size = 0
    for f in uploaded_files:
        if not f or not f.filename:
            continue
        ext = os.path.splitext(f.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            errors.append(f'File "{f.filename}": type not allowed. Accepted: PDF, JPG, PNG.')
            continue
        data = f.read()
        total_size += len(data)
        valid_files.append((f.filename, f.content_type or 'application/octet-stream', data))
    if total_size > MAX_TOTAL_UPLOAD:
        errors.append(f'Total attachment size exceeds 2 MB ({total_size / (1024*1024):.1f} MB uploaded).')

    if errors:
        for e in errors:
            flash(e, 'error')
        form_data = _build_form_data(request.form, items_data)
        return render_template('requester/new_pr.html', form=form_data), 422

    # --- Atomic save ---
    try:
        pr = PurchaseRequisition(
            title=title,
            requester_email=g.current_user_email,
            need_by_date=need_by_date,
            purchase_type=purchase_type,
            is_outage=is_outage,
            is_emergency=is_emergency,
            cost_code=cost_code,
            ea_number=ea_number,
            is_quote_attached=is_quote_attached,
            manager_approval_received=manager_approval_received,
            vendor=vendor,
        )
        db.session.add(pr)
        db.session.flush()
        pr.set_pr_number()

        for item in items_data:
            db.session.add(RequisitionItem(
                requisition_id=pr.id,
                quantity=item['quantity'],
                description=item['description'],
                part_number=item['part_number'],
                price=item['price'],
            ))

        for filename, content_type, data in valid_files:
            db.session.add(Attachment(
                requisition_id=pr.id,
                filename=filename,
                content_type=content_type,
                data=data,
                size=len(data),
            ))

        if valid_files:
            pr.is_quote_attached = True

        db.session.commit()
        flash(f'Purchase Requisition #{pr.pr_number} created successfully.', 'success')
        return redirect(url_for('requester.view_pr', pr_id=pr.id))

    except Exception:
        db.session.rollback()
        flash('An unexpected error occurred while saving. Please try again.', 'error')
        form_data = _build_form_data(request.form, items_data)
        return render_template('requester/new_pr.html', form=form_data), 500


@requester_bp.route('/mine')
def my_prs():
    prs = (
        PurchaseRequisition.query
        .filter_by(requester_email=g.current_user_email)
        .order_by(PurchaseRequisition.request_date.desc())
        .all()
    )
    return render_template('requester/my_prs.html', prs=prs)


@requester_bp.route('/<int:pr_id>')
def view_pr(pr_id):
    pr = PurchaseRequisition.query.get_or_404(pr_id)
    if not g.is_buyer and pr.requester_email != g.current_user_email:
        abort(403)
    return render_template('requester/view_pr.html', pr=pr)


@requester_bp.route('/<int:pr_id>/attachment/<int:att_id>')
def download_attachment(pr_id, att_id):
    pr = PurchaseRequisition.query.get_or_404(pr_id)
    if not g.is_buyer and pr.requester_email != g.current_user_email:
        abort(403)
    attachment = Attachment.query.filter_by(id=att_id, requisition_id=pr_id).first_or_404()
    return send_file(
        io.BytesIO(attachment.data),
        mimetype=attachment.content_type,
        as_attachment=True,
        download_name=attachment.filename,
    )
