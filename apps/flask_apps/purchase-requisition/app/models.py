from datetime import datetime, timezone
from app import db


class PurchaseRequisition(db.Model):
    __tablename__ = 'purchase_requisitions'

    id = db.Column(db.Integer, primary_key=True)
    pr_number = db.Column(db.String(10), unique=True, index=True)
    title = db.Column(db.String(200), nullable=False)
    requester_email = db.Column(db.String(200), nullable=False, index=True)
    request_date = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    need_by_date = db.Column(db.Date, nullable=False)
    purchase_type = db.Column(db.String(20), nullable=False)
    is_outage = db.Column(db.Boolean, default=False, nullable=False)
    is_emergency = db.Column(db.Boolean, default=False, nullable=False)
    cost_code = db.Column(db.String(12), nullable=False)
    ea_number = db.Column(db.String(50))
    is_quote_attached = db.Column(db.Boolean, default=False, nullable=False)
    manager_approval_received = db.Column(db.Boolean, default=False, nullable=False)
    vendor = db.Column(db.String(200))
    status = db.Column(db.String(20), default='Pending', nullable=False, index=True)

    items = db.relationship(
        'RequisitionItem',
        backref='requisition',
        cascade='all, delete-orphan',
        lazy=True,
    )
    comments = db.relationship(
        'Comment',
        backref='requisition',
        cascade='all, delete-orphan',
        lazy=True,
        order_by='Comment.created_at',
    )

    def set_pr_number(self):
        """Call after db.session.flush() to derive pr_number from assigned id."""
        self.pr_number = str(self.id).zfill(5)


class RequisitionItem(db.Model):
    __tablename__ = 'requisition_items'

    id = db.Column(db.Integer, primary_key=True)
    requisition_id = db.Column(
        db.Integer,
        db.ForeignKey('purchase_requisitions.id'),
        nullable=False,
    )
    quantity = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    part_number = db.Column(db.String(100))
    price = db.Column(db.Float, nullable=False)


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    requisition_id = db.Column(
        db.Integer,
        db.ForeignKey('purchase_requisitions.id'),
        nullable=False,
    )
    author_email = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
