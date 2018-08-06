Rest API Usage - v0
===================

The API contains two endpoints, one to save the Event Calls data and another one to retrieve the Bill for a phone number by period.

If the period is not informed, the last month of the current date will be used. You can't retrieve Bill information of the current period.

POST Event Calls
----------------

.. http:post:: /api/v0/call_events/

   Save the data of a call event.

   **Example request**:

   .. sourcecode:: http

      POST /api/v0/call_events/ HTTP/1.1
      Accept: application/json

      {
        "call_id": "1",
        "type": "start",
        "timestamp": "2018-09-01T04:12:34Z",
        "source": "11911111111",
        "destination": "11922222222"
      }

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json

   :<json string call_id: call event id unique for the call
   :<json string type: type of the call event being: ``start`` or ``end``
   :<json string timestamp: timestamp of this event (when it started or ended)
   :<json string source: the phone number making the call (only required for events of type ``start``)
   :<json string destination: the phone number receiving the call (only required for events of type ``start``)
   :statuscode 201: created
   :statuscode 400: invalid data (wrong format or fields missing)
   :statuscode 500: unexpected error


GET Bill
--------

.. http:get:: /api/v0/bills/(int:phone_number)/(int:month)/(int:year)/

   Bill detail for `phone_number` and period `month/year` (optional).

   **Example request**:

   .. sourcecode:: http

      GET /api/v0/bill/11911111111/ HTTP/1.1

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "subscriber": "14911111111",
        "period": "01/2018",
        "calls": [
          {
            "destination": "14922222222",
            "start_date": "2018-01-15",
            "start_time": "01:01:11Z",
            "duration": "1:23:01",
            "price": "0.36"
          },
          {
            "destination": "14933333333",
            "start_date": "2018-01-18",
            "start_time": "10:30:00Z",
            "duration": "2 days, 1:00:00",
            "price": "178.56"
          }
        ]
      }

   :query int phone_number: the number to retrieve the bill
   :query int month: month of the period (optional)
   :query int year: year of the period (optional)
   :statuscode 200: found the data for number and period
   :statuscode 400: invalid parameters
   :statuscode 500: unexpected error
