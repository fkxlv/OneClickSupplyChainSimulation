from marshmallow import Schema, fields, validate, EXCLUDE

class GraphEventSchema(Schema):
    """
    Single event in the coordination graph.
    """
    class Meta:
        unknown = EXCLUDE

    request_id = fields.String(required=True)

    timestamp = fields.String(required=True)

    from_agent = fields.String(required=True)
    to_agent = fields.String(required=True)

    event_type = fields.String(required=True)

    status = fields.String(
        required=True,
        validate=validate.OneOf(["success", "fail", "info"])
    )

    payload = fields.Dict(required=True)

