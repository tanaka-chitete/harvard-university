SELECT title FROM movies
JOIN stars ON movies.id = stars.movie_id
WHERE stars.person_id
IN (SELECT id FROM people 
WHERE name IN ("Johnny Depp", "Helena Bonham Carter"))
GROUP BY title HAVING COUNT(*) > 1;
