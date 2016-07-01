DROP TABLE IF EXISTS 'ENTRIES';

CREATE TABLE ENTRIES(
  eid integer primary key autoincrement,
	title string not null,
	text string not null
)