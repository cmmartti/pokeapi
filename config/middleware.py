from django.db import connection
from django.utils.log import getLogger
import re

logger = getLogger(__name__)

class QueryCountDebugMiddleware(object):
    """
    This middleware will log the number of queries run
    and the total time taken for each request (with a
    status code of 200). It does not currently support
    multi-db setups.
    """
    def process_response(self, request, response):
        if response.status_code == 200:
            total_time = 0

            for query in connection.queries:
                query_time = query.get("time")
                if query_time is None:
                    # django-debug-toolbar monkeypatches the connection
                    # cursor wrapper and adds extra information in each
                    # item in connection.queries. The query time is stored
                    # under the key "duration" rather than "time" and is
                    # in milliseconds, not seconds.
                    query_time = query.get("duration", 0) / 1000
                total_time += float(query_time)

            logger.debug("%s queries in %s seconds" % (len(connection.queries), total_time))
        return response

class QueryDebugMiddleware(object):
    """
    This middleware will log each query that is run.
    """
    def process_response(self, request, response):
        if response.status_code == 200:
            for i, query in enumerate(connection.queries):
                sql = re.split(r"(SELECT|FROM|WHERE|GROUP BY|ORDER BY|INNER JOIN|LIMIT|ON|LEFT OUTER JOIN)", query["sql"])
                if not sql[0]:
                    sql = sql[1:]

                # Join every other line
                string = ""
                for i, line in enumerate(sql):
                    if i % 2:
                        string += "%s\n" % line
                    else:
                        string += line

                # Remove quotation marks
                string = string.replace('"', "")

                # Put each select clause on its own line
                regex = re.compile("(, )(?=.*\n*FROM)")
                string = regex.sub(",\n       ", string)

                # Put each AND clause on its own line
                regex = re.compile(" AND ")
                string = regex.sub(" \n  AND ", string)

                # Indent every other line
                # sql = [
                #     (" " if i % 2 else "") + x
                #     for i, x in enumerate(sql)
                # ]

                logger.debug("{} ({} seconds)\n{}".format(i, query["time"], string))
        return response
