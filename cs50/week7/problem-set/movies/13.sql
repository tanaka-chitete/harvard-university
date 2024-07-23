SELECT DISTINCT(name) FROM people
WHERE name IS NOT 'Kevin Bacon' AND id IN
(SELECT person_id FROM stars WHERE movie_id IN
(SELECT movie_id FROM stars WHERE person_id IN
(SELECT id FROM people WHERE name IS 'Kevin Bacon' AND
(SELECT id FROM people WHERE birth = 1958))))
GROUP BY name HAVING COUNT(*) = 1
ORDER BY name;