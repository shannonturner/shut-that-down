CREATE TABLE persons
(
  id serial NOT NULL,
  display_name character varying,
  first_name character varying,
  last_name character varying,
  littlesis_name character varying,
  littlesis_id character varying,
  bioguide_id character varying,
  sunlight_id character varying,
  crp_id character varying,
  type integer,
  gender character(1),
  party character varying,
  state character(2),
  CONSTRAINT "PK_persons" PRIMARY KEY (id)
);

CREATE TABLE organizations
(
  id serial NOT NULL,
  name character varying,
  littlesis_name character varying,
  littlesis_id character varying,
  sunlight_id character varying,
  crp_id character varying,
  contact_tw character varying,
  contact_www character varying,
  contact_ph character varying,
  contact_email character varying,
  CONSTRAINT "PK_organizations" PRIMARY KEY (id)
);


CREATE TABLE quotes
(
  id serial NOT NULL,
  quote_text character varying,
  quote_context character varying,
  quoted_in integer,
  quote_date date,
  who_said integer,
  at_event character varying,
  quote_url character varying,
  CONSTRAINT "PK_quotes" PRIMARY KEY (id)
);

CREATE TABLE issues
(
  id serial NOT NULL,
  issue character varying,
  CONSTRAINT "PK_issues" PRIMARY KEY (id)
);

CREATE TABLE voter_turnout
(
  year integer NOT NULL,
  state_abbrev character (2) NOT NULL,
  state character varying,
  vep_turnout_rate real,
  PRIMARY KEY (year, state_abbrev)
);

CREATE TABLE quote_issues
(
   quote_id integer, 
   issue_id integer, 
   FOREIGN KEY (quote_id) REFERENCES quotes (id) ON UPDATE NO ACTION ON DELETE NO ACTION, 
   FOREIGN KEY (issue_id) REFERENCES issues (id) ON UPDATE NO ACTION ON DELETE NO ACTION
);

 CREATE TABLE recent_activity
 (
   id serial NOT NULL,
   event integer,
   date date,
   PRIMARY KEY (id)
 );
 
  CREATE TABLE bills
 (
   id serial NOT NULL,
   bill_number character varying,
   bill_name character varying,
   bad_position integer, -- 0: oppose, 1: support
   our_position integer, -- 0: oppose, 1: support
   PRIMARY KEY (id)
 );
 
 CREATE TABLE bill_issues
 (
   bill_id integer NOT NULL,
   issue_id integer NOT NULL,
   FOREIGN KEY (bill_id) REFERENCES bills (id) ON UPDATE NO ACTION ON DELETE NO ACTION,
   FOREIGN KEY (issue_id) REFERENCES issues (id) ON UPDATE NO ACTION ON DELETE NO ACTION
 );
 
 CREATE TABLE bill_positions
 (
   id serial NOT NULL,
   bill_id integer,
   person_id integer,
   position integer,
   action integer,
   FOREIGN KEY (bill_id) REFERENCES bills (id) ON UPDATE NO ACTION ON DELETE NO ACTION,
   FOREIGN KEY (person_id) REFERENCES persons (id) ON UPDATE NO ACTION ON DELETE NO ACTION
   
 );
 
 CREATE TABLE connections
 (
 	-- This table is for other types of connections that aren't found on a mutual vote on a bill, being in the same party, etc.
 	-- A good use for it is: a campaign staffer would be related to the offices they worked for, or a media endorsement
   id serial NOT NULL,
   first_person_id integer,
   second_person_id integer,
   connection character varying
);
 

CREATE TABLE error_log
(

  id serial NOT NULL,
  exception_type character varying, 
  exception_value character varying, 
  traceback character varying, 
  time date,
  PRIMARY KEY (id)
);

 
CREATE FUNCTION insert_quotes_update() RETURNS trigger as $insert_quotes_update$
 	BEGIN
 		insert into recent_activity (event, date) VALUES (1, NOW());
 		RETURN NEW;
 	END;
 $insert_quotes_update$ LANGUAGE plpgsql;
 
 CREATE TRIGGER updated_on AFTER insert on quotes
 FOR EACH ROW
 EXECUTE PROCEDURE insert_quotes_update();
 
 CREATE FUNCTION insert_persons_update() RETURNS trigger as $insert_persons_update$
 	BEGIN
 		insert into recent_activity (event, date) VALUES (2, NOW());
 		RETURN NEW;
 	END;
 $insert_persons_update$ LANGUAGE plpgsql;
 
 CREATE TRIGGER updated_on AFTER insert on persons
 FOR EACH ROW
 EXECUTE PROCEDURE insert_persons_update();
 
CREATE FUNCTION insert_org_update() RETURNS trigger as $insert_org_update$
 	BEGIN
 		insert into recent_activity (event, date) VALUES (3, NOW());
 		RETURN NEW;
 	END;
 $insert_org_update$ LANGUAGE plpgsql;
 
 CREATE TRIGGER updated_on AFTER insert on organizations
 FOR EACH ROW
 EXECUTE PROCEDURE insert_org_update(); 
 
 -- If you import anything outside of an INSERT statement, you'll need to run this on each table that you import to
 -- 	this way, Postgres will update its sequence key and it won't try to insert to IDs that already exist
 --	in this example, replace persons with the table name
 
 -- select setval('persons_id_seq', (SELECT MAX(id) from persons)+1)
 -- select setval('quotes_id_seq', (SELECT MAX(id) from quotes)+1)