SELECT AVG(ticket_count) as average_passengers
FROM (
    SELECT COUNT(tickets.ticket_number) as ticket_count
    FROM tickets 
    JOIN flights ON tickets.flight_id = flights.flight_id
    WHERE flights.status = 'Landed'
    GROUP BY tickets.flight_id
) as counts_table;	

SELECT planes.manufacturer, planes.size, 
    SUM(
        CASE 
            WHEN orders.status = 'Completed' AND tickets.class_type = 'Economy' THEN tickets.price
            
            WHEN orders.status = 'CancelledByCustomer' AND tickets.class_type = 'Economy' THEN tickets.price * 0.05
            
            WHEN orders.status = 'Active' 
				 AND tickets.class_type = 'Economy'
                 AND flights.departure_time <= NOW() + INTERVAL 36 HOUR 
                 AND flights.departure_time > NOW() 
                 THEN tickets.price
            ELSE 0 
        END
    ) AS revenue_from_economy,
        SUM(
        CASE 
            WHEN orders.status = 'Completed' AND tickets.class_type = 'Business' THEN tickets.price
            
            WHEN orders.status = 'CancelledByCustomer' AND tickets.class_type = 'Business' THEN tickets.price * 0.05
            
            WHEN orders.status = 'Active' 
				 AND tickets.class_type = 'Business'
                 AND flights.departure_time <= NOW() + INTERVAL 36 HOUR 
                 AND flights.departure_time > NOW() 
                 THEN tickets.price
            ELSE 0 
        END
    ) AS revenue_from_business
FROM tickets
JOIN planes ON tickets.plane_id = planes.plane_id
JOIN orders ON tickets.order_code = orders.order_code
JOIN flights ON tickets.flight_id = flights.flight_id
GROUP BY planes.manufacturer, planes.size, tickets.class_type
ORDER BY planes.manufacturer ASC, planes.size ASC, tickets.class_type ASC;


SELECT attendants.id_num, attendants.first_name, attendants.last_name, 'Attendant' AS Job_Title,
	SUM(CASE WHEN TIMESTAMPDIFF(MINUTE, departure_time, landing_time) <= 360 THEN TIMESTAMPDIFF(MINUTE, departure_time, landing_time) / 60.0 ELSE 0 END) AS Hours_On_Short_Flights,
    SUM(CASE WHEN TIMESTAMPDIFF(MINUTE, departure_time, landing_time) > 360 THEN TIMESTAMPDIFF(MINUTE, departure_time, landing_time) / 60.0 ELSE 0 END) AS Hours_On_Long_Flights
FROM attendants JOIN attendantsonflights ON attendants.id_num = attendantsonflights.attendant_id JOIN flights ON attendantsonflights.flight_id = flights.flight_id
GROUP BY id_num, first_name, last_name

UNION ALL

SELECT pilots.id_num, pilots.first_name, pilots.last_name, 'Pilot' AS Job_Title,
	SUM(CASE WHEN TIMESTAMPDIFF(MINUTE, departure_time, landing_time) <= 360 THEN TIMESTAMPDIFF(MINUTE, departure_time, landing_time) / 60.0 ELSE 0 END) AS Hours_On_Short_Flights,
    SUM(CASE WHEN TIMESTAMPDIFF(MINUTE, departure_time, landing_time) > 360 THEN TIMESTAMPDIFF(MINUTE, departure_time, landing_time) / 60.0 ELSE 0 END) AS Hours_On_Long_Flights
FROM pilots JOIN pilotsonflights ON pilots.id_num = pilotsonflights.pilot_id JOIN flights ON pilotsonflights.flight_id = flights.flight_id
GROUP BY id_num, first_name, last_name;



SELECT DATE_FORMAT(flights.departure_time, '%M %Y') AS month_year,
    CONCAT((SUM(CASE WHEN orders.status = 'CancelledByCustomer' THEN 1 ELSE 0 END) / COUNT(*) * 100), '%') AS percentage_cancelled

FROM orders JOIN tickets ON orders.order_code = tickets.order_code JOIN flights ON tickets.flight_id = flights.flight_id
GROUP BY YEAR(flights.departure_time), MONTH(flights.departure_time), month_year
ORDER BY YEAR(flights.departure_time) ASC, MONTH(flights.departure_time) ASC;
  
    
SELECT stats.plane_id, stats.month_year, stats.executed_flights, stats.cancelled_flights, stats.usage_percentage,
    (
        SELECT CONCAT(f2.src_city, ' - ', f2.dst_city)
        FROM flights AS f2
        WHERE f2.plane_id = stats.plane_id 
          AND YEAR(f2.departure_time) = stats.flight_year
          AND MONTH(f2.departure_time) = stats.flight_month
        GROUP BY f2.src_city, f2.dst_city
        ORDER BY COUNT(*) DESC
        LIMIT 1
    ) AS dominant_route
FROM (
    SELECT planes.plane_id, YEAR(flights.departure_time) AS flight_year, MONTH(flights.departure_time) AS flight_month, DATE_FORMAT(flights.departure_time, '%M %Y') AS month_year,
        SUM(CASE WHEN flights.status != 'Cancelled' THEN 1 ELSE 0 END) AS executed_flights,
        SUM(CASE WHEN flights.status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_flights,
        CONCAT(ROUND(COUNT(DISTINCT CASE WHEN flights.status = 'Landed' THEN DATE(flights.departure_time) END) / 30 * 100, 2), '%') AS usage_percentage
    FROM planes 
    JOIN flights ON planes.plane_id = flights.plane_id
    GROUP BY planes.plane_id, flight_year, flight_month, month_year
) AS stats
ORDER BY stats.flight_year ASC, stats.flight_month ASC;




