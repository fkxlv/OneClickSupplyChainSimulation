from marshmallow import Schema, fields, validate, EXCLUDE
from .planner import PlannerOutputSchema
from .sourcing import SourcingResultSchema


class ExecutionRequestSchema(Schema):
    """
    Input to Execution agent.
    """
    class Meta:
        unknown = EXCLUDE

    planner_output = fields.Nested(PlannerOutputSchema, required=True)
    sourcing_result = fields.Nested(SourcingResultSchema, required=True)

class ContractTermsSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    total_price = fields.Float(required=True)
    lead_time_days = fields.Integer(required=True)

class ExecutionResultSchema(Schema):
    """
    Final outcome of execution.
    """
    class Meta:
        unknown = EXCLUDE

    request_id = fields.String(required=True)

    status = fields.String(
        required=True,
        validate=validate.OneOf(["success", "failed"])
    )

    supplier_id = fields.String(allow_none=True)

    contract_terms = fields.Nested(
        ContractTermsSchema,
        allow_none=True
    )

    failure_reason = fields.String(allow_none=True)
