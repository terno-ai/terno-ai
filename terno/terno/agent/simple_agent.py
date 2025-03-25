from terno.pipeline.step import Step
from terno.pipeline.pipeline import Pipeline


class QueryUnderstandingStep(Step):
    def execute(self, context):
        print('execute query unde')
        llm = context['llm']
        user_query = context['user_query']
        db_schema = context['db_schema']

        prompt = f"""Analyze this natural language query and extract key information:
Query: {user_query}
Schema: {db_schema}

1. What are the main entities/tables involved?
2. What are the key conditions or filters?
3. What aggregations or calculations are needed?
4. Are there any temporal aspects (dates, time periods)?
5. What should be displayed in the results?

Provide your analysis in a structured format."""
        response = llm.generate(prompt)
        context['query_analysis'] = response
        print(response)
        print('QueryUnderstandingStep', context)
        return context


class SchemaAnalysisStep(Step):
    def execute(self, context):
        print('execute query analy')
        llm = context['llm']
        analysis = context['query_analysis']
        db_schema = context['db_schema']

        prompt = f"""Based on the query analysis and database schema, determine:
Analysis: {analysis}
Schema: {db_schema}

1. Which specific tables and columns are needed?
2. What joins are required between these tables?
3. Are all required fields available in the schema?
4. Are there any potential data type conversions needed?
5. What indexes or optimizations might be helpful?

Provide a technical plan for the query."""

        response = llm.generate(prompt)
        context['schema_plan'] = response
        print('SchemaAnalysisStep', response)
        return context


class SQLGenerationStep(Step):
    def execute(self, context):
        print('execute query gen')
        llm = context['llm']
        analysis = context['query_analysis']
        plan = context['schema_plan']
        db_schema = context['db_schema']
        dialect = context.get('dialect', 'postgresql')
        user_query = context['user_query']

        prompt = f"""Generate an optimized SQL query based on:
Analysis: {analysis}
Technical Plan: {plan}
Schema: {db_schema}
Dialect: {dialect}
User Query: {user_query}

Requirements:
1. Follow the technical plan
2. Use proper table/column names from schema
3. Include appropriate joins
4. Add necessary filters
5. Optimize for performance
6. Follow {dialect} syntax
7. SQL Query should answer user prompt exactly
8. Unnecessary optional joins, and filters must be avoided.

Return only the SQL query without any explanation."""

        sql = llm.generate(prompt)
        context['generated_sql'] = sql
        print('SQLGenerationStep', sql)
        return context


class SQLValidationStep(Step):
    def execute(self, context):
        print('execute query val')
        llm = context['llm']
        sql = context['generated_sql']
        db_schema = context['db_schema']

        prompt = f"""Validate this SQL query:
SQL: {sql}
Schema: {db_schema}

Check for:
1. Syntax correctness
2. Proper table/column references
3. Join conditions
4. Filter logic
5. Potential performance issues

If there are issues, provide a corrected query. Otherwise, confirm it's valid."""

        response = llm.generate(prompt)
        if "valid" not in response.lower():
            # Extract corrected SQL from response
            corrected_sql = extract_sql_from_response(response)
            context['generated_sql'] = corrected_sql
            context['validation_message'] = response
        else:
            context['validation_message'] = "SQL query validated successfully"
        print('SQLValidationStep', response)
        return context


def extract_sql_from_response(response):
    # Simple extraction - assumes the SQL is between triple backticks
    # Could be made more sophisticated based on actual LLM response format
    start = response.find('```sql\n')
    if start != -1:
        end = response.find('```', start + 7)
        if end != -1:
            return response[start + 7:end].strip()
    return response


def create_sql_agent_pipeline(llm, user_query, db_schema, datasource):
    """Creates a pipeline for the SQL generation agent"""
    pipeline = Pipeline()

    # Initialize context
    context = {
        'llm': llm,
        'user_query': user_query,
        'db_schema': db_schema,
        'datasource': datasource,
        'dialect': datasource.dialect_name
    }

    # Add steps to pipeline
    pipeline.add_step(QueryUnderstandingStep())
    pipeline.add_step(SchemaAnalysisStep())
    pipeline.add_step(SQLGenerationStep())
    pipeline.add_step(SQLValidationStep())

    pipeline.set_context(context)
    return pipeline
