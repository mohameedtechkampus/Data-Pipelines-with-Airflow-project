from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class LoadDimensionOperator(BaseOperator):
    insert_sql="""
    INSERT INTO
    {table} 
    {load_sql_stmt}
    """
    
    truncate_sql="""
    TRUNCATE TABLE {load_sql_stmt}
    """

    ui_color = '#80BD9E'

    @apply_defaults
    def __init__(self,
                 redshift_conn_id="",
                 table="",
                 load_sql_stmt="",      
                 append_only=False,
                 *args, **kwargs):

        super(LoadDimensionOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id
        self.table = table
        self.load_sql_stmt = load_sql_stmt
        self.append_only = append_only

    def execute(self, context):
        try:
            redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)
            self.log.info("Redshift hook defined")
        except AirflowError as e:
            self.log.error(e)
        
        
        if not self.append_only:
            self.log.info(f"Truncating table {self.table}")
            redshift.run(LoadDimensionOperator.truncate_sql.format(table=self.table))
        
      
        self.log.info(f"Inserting values on {self.table}")
        redshift.run(LoadDimensionOperator.insert_sql.format(table=self.table, load_sql_stmt=self.load_sql_stmt))