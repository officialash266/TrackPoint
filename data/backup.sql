BEGIN TRANSACTION;
CREATE TABLE competitors (
                competitor_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL CHECK(length(name) BETWEEN 1 AND 50),
                year_group TEXT NOT NULL CHECK(year_group IN ('7', '8', '9', '10', '11', '12')),
                house TEXT NOT NULL CHECK(house IN ('Midson', 'Darvall', 'Harris', 'Terry'))
            );
INSERT INTO "competitors" VALUES(1,'Ali Khan','12','Midson');
INSERT INTO "competitors" VALUES(2,'Noah Smith','10','Darvall');
INSERT INTO "competitors" VALUES(3,'Lucas Chen','11','Harris');
INSERT INTO "competitors" VALUES(4,'Ryan Patel','9','Terry');
INSERT INTO "competitors" VALUES(5,'Ethan Brown','8','Midson');
INSERT INTO "competitors" VALUES(6,'Liam Wilson','7','Darvall');
INSERT INTO "competitors" VALUES(7,'Oliver Nguyen','10','Harris');
INSERT INTO "competitors" VALUES(8,'Jack Thompson','12','Terry');
INSERT INTO "competitors" VALUES(9,'Henry Davis','11','Midson');
INSERT INTO "competitors" VALUES(10,'William Lee','9','Darvall');
INSERT INTO "competitors" VALUES(11,'James Martin','8','Harris');
INSERT INTO "competitors" VALUES(12,'Thomas Walker','7','Terry');
INSERT INTO "competitors" VALUES(13,'Benjamin Young','12','Midson');
INSERT INTO "competitors" VALUES(14,'Samuel Moore','10','Darvall');
INSERT INTO "competitors" VALUES(15,'Daniel White','11','Harris');
INSERT INTO "competitors" VALUES(16,'Max Harris','9','Terry');
CREATE TABLE events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_name TEXT NOT NULL CHECK(length(event_name) BETWEEN 1 AND 40),
                event_type TEXT NOT NULL CHECK(event_type IN ('Track', 'Field')),
                age_group TEXT NOT NULL CHECK(length(age_group) BETWEEN 1 AND 10)
            );
INSERT INTO "events" VALUES(1,'100m Sprint','Track','Open');
INSERT INTO "events" VALUES(2,'Long Jump','Field','Open');
INSERT INTO "events" VALUES(3,'400m Run','Track','U16');
INSERT INTO "events" VALUES(4,'Shot Put','Field','Open');
INSERT INTO "events" VALUES(5,'200m Sprint','Track','U14');
INSERT INTO "events" VALUES(6,'High Jump','Field','U16');
INSERT INTO "events" VALUES(7,'800m Run','Track','Open');
INSERT INTO "events" VALUES(8,'Discus','Field','U14');
CREATE TABLE results (
                result_id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                competitor_id INTEGER NOT NULL,
                placing INTEGER NOT NULL CHECK(placing BETWEEN 1 AND 8),
                result_value TEXT NOT NULL CHECK(length(result_value) BETWEEN 1 AND 15),
                points_awarded INTEGER NOT NULL CHECK(points_awarded IN (0, 1, 2, 4, 6, 8)),
                FOREIGN KEY(event_id) REFERENCES events(event_id),
                FOREIGN KEY(competitor_id) REFERENCES competitors(competitor_id),
                UNIQUE(event_id, competitor_id)
            );
INSERT INTO "results" VALUES(1,1,1,1,'12.42 s',8);
INSERT INTO "results" VALUES(2,1,2,2,'12.66 s',6);
INSERT INTO "results" VALUES(3,1,3,3,'12.91 s',4);
INSERT INTO "results" VALUES(4,1,4,4,'13.10 s',2);
INSERT INTO "results" VALUES(5,2,5,2,'5.21 m',6);
INSERT INTO "results" VALUES(6,2,6,1,'5.48 m',8);
INSERT INTO "results" VALUES(7,2,7,4,'4.95 m',2);
INSERT INTO "results" VALUES(8,2,8,3,'5.10 m',4);
INSERT INTO "results" VALUES(9,3,9,1,'56.22 s',8);
INSERT INTO "results" VALUES(10,3,10,3,'57.43 s',4);
INSERT INTO "results" VALUES(11,3,11,2,'56.89 s',6);
INSERT INTO "results" VALUES(12,3,12,5,'59.11 s',1);
INSERT INTO "results" VALUES(13,4,13,3,'9.32 m',4);
INSERT INTO "results" VALUES(14,4,14,2,'9.55 m',6);
INSERT INTO "results" VALUES(15,4,15,1,'9.87 m',8);
INSERT INTO "results" VALUES(16,4,16,4,'8.96 m',2);
INSERT INTO "results" VALUES(17,5,1,2,'25.18 s',6);
INSERT INTO "results" VALUES(18,5,6,4,'26.02 s',2);
INSERT INTO "results" VALUES(19,5,11,1,'24.88 s',8);
INSERT INTO "results" VALUES(20,5,16,3,'25.57 s',4);
INSERT INTO "results" VALUES(21,6,5,1,'1.62 m',8);
INSERT INTO "results" VALUES(22,6,10,3,'1.55 m',4);
INSERT INTO "results" VALUES(23,6,15,2,'1.59 m',6);
INSERT INTO "results" VALUES(24,6,8,5,'1.48 m',1);
INSERT INTO "results" VALUES(25,7,9,2,'133.20 s',6);
INSERT INTO "results" VALUES(26,7,14,1,'131.76 s',8);
INSERT INTO "results" VALUES(27,7,3,4,'136.45 s',2);
INSERT INTO "results" VALUES(28,7,12,3,'134.82 s',4);
INSERT INTO "results" VALUES(29,8,13,1,'28.40 m',8);
INSERT INTO "results" VALUES(30,8,2,3,'26.85 m',4);
INSERT INTO "results" VALUES(31,8,7,2,'27.66 m',6);
INSERT INTO "results" VALUES(32,8,4,4,'25.90 m',2);
CREATE TABLE users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE CHECK(length(username) BETWEEN 3 AND 20),
                password_hash TEXT NOT NULL CHECK(length(password_hash) = 64),
                role TEXT NOT NULL CHECK(role IN ('Admin', 'Staff', 'Student')),
                competitor_id INTEGER,
                FOREIGN KEY(competitor_id) REFERENCES competitors(competitor_id)
            );
INSERT INTO "users" VALUES(1,'admin','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9','Admin',NULL);
INSERT INTO "users" VALUES(2,'staff','10176e7b7b24d317acfcf8d2064cfd2f24e154f7b5a96603077d5ef813d6a6b6','Staff',NULL);
INSERT INTO "users" VALUES(3,'student','703b0a3d6ad75b649a28adde7d83c6251da457549263bc7ff45ec709b0a8448b','Student',1);
CREATE UNIQUE INDEX unique_student_competitor
            ON users(competitor_id)
            WHERE role = 'Student' AND competitor_id IS NOT NULL
        ;
CREATE TRIGGER validate_competitor_insert
            BEFORE INSERT ON competitors
            WHEN length(trim(NEW.name)) NOT BETWEEN 1 AND 50
              OR NEW.year_group NOT IN ('7', '8', '9', '10', '11', '12')
              OR NEW.house NOT IN ('Midson', 'Darvall', 'Harris', 'Terry')
            BEGIN SELECT RAISE(ABORT, 'Invalid competitor data'); END;
CREATE TRIGGER validate_competitor_update
            BEFORE UPDATE ON competitors
            WHEN length(trim(NEW.name)) NOT BETWEEN 1 AND 50
              OR NEW.year_group NOT IN ('7', '8', '9', '10', '11', '12')
              OR NEW.house NOT IN ('Midson', 'Darvall', 'Harris', 'Terry')
            BEGIN SELECT RAISE(ABORT, 'Invalid competitor data'); END;
CREATE TRIGGER validate_user_insert
            BEFORE INSERT ON users
            WHEN length(NEW.username) NOT BETWEEN 3 AND 20
              OR NEW.username GLOB '*[^A-Za-z0-9_]*'
              OR length(NEW.password_hash) != 64
              OR NEW.role NOT IN ('Admin', 'Staff', 'Student')
              OR (NEW.role = 'Student' AND NEW.competitor_id IS NULL)
              OR (NEW.role != 'Student' AND NEW.competitor_id IS NOT NULL)
            BEGIN SELECT RAISE(ABORT, 'Invalid user data'); END;
CREATE TRIGGER validate_event_insert
            BEFORE INSERT ON events
            WHEN length(trim(NEW.event_name)) NOT BETWEEN 1 AND 40
              OR NEW.event_type NOT IN ('Track', 'Field')
              OR length(trim(NEW.age_group)) NOT BETWEEN 1 AND 10
            BEGIN SELECT RAISE(ABORT, 'Invalid event data'); END;
CREATE TRIGGER validate_event_update
            BEFORE UPDATE ON events
            WHEN length(trim(NEW.event_name)) NOT BETWEEN 1 AND 40
              OR NEW.event_type NOT IN ('Track', 'Field')
              OR length(trim(NEW.age_group)) NOT BETWEEN 1 AND 10
            BEGIN SELECT RAISE(ABORT, 'Invalid event data'); END;
CREATE TRIGGER validate_result_insert
            BEFORE INSERT ON results
            WHEN NEW.placing NOT BETWEEN 1 AND 8
              OR length(trim(NEW.result_value)) NOT BETWEEN 1 AND 15
              OR NEW.points_awarded != CASE NEW.placing
                    WHEN 1 THEN 8 WHEN 2 THEN 6 WHEN 3 THEN 4
                    WHEN 4 THEN 2 WHEN 5 THEN 1 ELSE 0 END
            BEGIN SELECT RAISE(ABORT, 'Invalid result data'); END;
CREATE TRIGGER validate_result_update
            BEFORE UPDATE ON results
            WHEN NEW.placing NOT BETWEEN 1 AND 8
              OR length(trim(NEW.result_value)) NOT BETWEEN 1 AND 15
              OR NEW.points_awarded != CASE NEW.placing
                    WHEN 1 THEN 8 WHEN 2 THEN 6 WHEN 3 THEN 4
                    WHEN 4 THEN 2 WHEN 5 THEN 1 ELSE 0 END
            BEGIN SELECT RAISE(ABORT, 'Invalid result data'); END;
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('competitors',16);
INSERT INTO "sqlite_sequence" VALUES('users',3);
INSERT INTO "sqlite_sequence" VALUES('events',8);
INSERT INTO "sqlite_sequence" VALUES('results',32);
COMMIT;
