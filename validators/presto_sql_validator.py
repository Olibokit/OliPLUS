class PrestoDBSQLValidator(BaseSQLValidator):
    """Validate SQL queries using Presto's EXPLAIN (TYPE VALIDATE)"""

    name = "PrestoDBSQLValidator"

    @classmethod
    def validate_statement(
        cls,
        statement: SQLStatement,
        database: Database,
        cursor: Any,
    ) -> SQLValidationAnnotation | None:
        from pyhive.exc import DatabaseError

        sql = f"EXPLAIN (TYPE VALIDATE) {database.mutate_sql_based_on_config(str(statement))}"
        db_engine_spec = database.db_engine_spec

        try:
            db_engine_spec.execute(cursor, sql, database)
            while True:
                stats = cursor.poll().get("stats", {})
                if stats.get("state") == "FINISHED":
                    break
                time.sleep(0.2)
            db_engine_spec.fetch_data(cursor, MAX_ERROR_ROWS)
            return None

        except DatabaseError as db_error:
            return cls._parse_presto_error(db_error)

        except Exception as ex:
            logger.exception("Unexpected error during Presto validation: %s", str(ex))
            raise

    @staticmethod
    def _parse_presto_error(db_error: Exception) -> SQLValidationAnnotation:
        args = db_error.args
        if not args:
            raise PrestoSQLValidationError("No error details provided") from db_error

        if isinstance(args[0], str):
            raise PrestoSQLValidationError(args[0]) from db_error

        if not isinstance(args[0], dict):
            raise PrestoSQLValidationError("Unexpected error format") from db_error

        error_info = args[0]
        message = error_info.get("message", "Unknown Presto error")
        location = error_info.get("errorLocation", {})

        return SQLValidationAnnotation(
            message=message + ("\n(Error location unknown)" if not location else ""),
            line_number=location.get("lineNumber", 1),
            start_column=location.get("columnNumber", 1),
            end_column=location.get("columnNumber", 1),
        )

    @classmethod
    def validate(
        cls,
        sql: str,
        catalog: str | None,
        schema: str | None,
        database: Database,
    ) -> list[SQLValidationAnnotation]:
        parsed_script = SQLScript(sql, engine=database.db_engine_spec.engine)
        annotations: list[SQLValidationAnnotation] = []

        with database.get_sqla_engine(
            catalog=catalog,
            schema=schema,
            source=QuerySource.SQL_LAB,
        ) as engine, closing(engine.raw_connection()) as conn:
            cursor = conn.cursor()
            for statement in parsed_script.statements:
                annotation = cls.validate_statement(statement, database, cursor)
                if annotation:
                    annotations.append(annotation)

        logger.debug("Validation found %i error(s)", len(annotations))
        return annotations
