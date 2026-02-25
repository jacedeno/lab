from datetime import datetime, timedelta, timezone

from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class LoginPin(db.Model):
    __tablename__ = 'login_pins'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), nullable=False, index=True)
    pin_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    expires_at = db.Column(db.DateTime, nullable=False)
    attempts = db.Column(db.Integer, default=0, nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)

    def set_pin(self, pin):
        self.pin_hash = generate_password_hash(pin)
        self.expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

    def check_pin(self, pin):
        return check_password_hash(self.pin_hash, pin)

    @property
    def is_expired(self):
        now = datetime.now(timezone.utc)
        exp = self.expires_at if self.expires_at.tzinfo else self.expires_at.replace(tzinfo=timezone.utc)
        return now > exp

    @property
    def is_valid(self):
        return not self.used and not self.is_expired and self.attempts < 5


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
    attachments = db.relationship(
        'Attachment',
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
    price = db.Column(db.Float, nullable=True)


class Attachment(db.Model):
    __tablename__ = 'attachments'

    id = db.Column(db.Integer, primary_key=True)
    requisition_id = db.Column(
        db.Integer,
        db.ForeignKey('purchase_requisitions.id'),
        nullable=False,
    )
    filename = db.Column(db.String(255), nullable=False)
    content_type = db.Column(db.String(100), nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)
    size = db.Column(db.Integer, nullable=False)
    uploaded_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


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
