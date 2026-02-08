from marshmallow import Schema, fields, validate, EXCLUDE

class ConstraintsSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    max_budget = fields.Float(allow_none=True)
    deadline_days = fields.Integer(allow_none=True)
    region = fields.String(allow_none=True)


class PlannerOutputSchema(Schema):
    """
    Output of Planner agent after interpreting user intent.
    """
    class Meta:
        unknown = EXCLUDE

    request_id = fields.String(required=True)
    product = fields.String(required=True)
    quantity = fields.Float(required=True, validate=validate.Range(min=1))

    constraints = fields.Nested(ConstraintsSchema, required=True)

    heuristic = fields.String(
        required=True,
        validate=validate.OneOf(["cost", "deadline"])
    )

    missing_information = fields.List(
        fields.String(),
        required=True
    )

    checklist = fields.List(
        fields.String(),
        required=True,
        validate=validate.Length(min=1)
    )

    reasoning_summary = fields.String(allow_none=True)

class PlannerDecisionSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    status = fields.String(
        required=True,
        validate=validate.OneOf(["needs_more_info", "ready"])
    )

    planner_output = fields.Nested(PlannerOutputSchema, required=True)
