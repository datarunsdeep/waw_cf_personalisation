import smtplib
import constants as const
from google.cloud import bigquery

def sf_query(request):
	# instantiate a bigquery client connection
    bq_client = bigquery.Client()
    
    # Set CORS to enable GTM origin
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }

        return ('', 204, headers)

    headers = {
        'Access-Control-Allow-Origin': '*'
    }
    
    # parse the http input containing GA client id
    request_json = request.get_json()
    print(request_json['message'])
    
    # create the sql query with the input id
    query = """
    SELECT first_name, company, sales_rep 
    FROM `your-bigquery.dataset.table` 
    WHERE ga_id = '{}'
    """.format(request_json['message'])
    print(query)
    
    # run the query on bigquery
    query_job = bq_client.query(query)
    results = query_job.result()
    
    # put results in three variables
    # note: BigQuery query returns RowIterator object; to access
    # the contents we have to loop over the iterator.
    name = ''
    company = ''
    sales_rep = ''
    for row in results:
        print("name is {} , sales rep is {} ".format(row.first_name, row.sales_rep))
        name = row.first_name
        company = row.company
        sales_rep = row.sales_rep
        
    # concatenate result vars into one string and return it
    # (because returning tuples caused 500 server errors)
    res = name + ',' + sales_rep
    
    # Set up SMTP connection for email
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(const.email, const.password)
 
    msg = "Hi {}, your prospect {} from {} has just viewed your website.".format(sales_rep, name, company)
    server.sendmail(const.email, const.email, msg)
    server.quit()
    return (res,200,headers)
