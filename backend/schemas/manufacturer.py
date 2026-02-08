from marshmallow import Schema, fields, EXCLUDE
from .execution import ContractTermsSchema


class ManufacturerNegotiationRequestSchema(Schema):
    """
    Offer sent to manufacturer.
    """
    class Meta:
        unknown = EXCLUDE

    request_id = fields.String(required=True)

    supplier = fields.Dict(required=True)  # supplier metadata

    offer_terms = fields.Nested(
        ContractTermsSchema,
        required=True
    )

    message = fields.String(allow_none=True)

class ManufacturerReplySchema(Schema):
    """
    Manufacturer response to an offer.
    """
    class Meta:
        unknown = EXCLUDE

    status = fields.String(
        required=True,
        validate=validate.OneOf(["accept", "reject", "counter"])
    )

    counter_terms = fields.Nested(
        ContractTermsSchema,
        allow_none=True
    )

    message = fields.String(allow_none=True)

