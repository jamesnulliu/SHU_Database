CREATE TABLE IF NOT EXISTS colleges (
  id INT(2) ZEROFILL NOT NULL UNIQUE AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  address VARCHAR(255) NOT NULL,
  telephone VARCHAR(255) NOT NULL,
  PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS students (
  id INT(4) ZEROFILL NOT NULL UNIQUE AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  sex VARCHAR(255) NOT NULL,
  birthday VARCHAR(255) NOT NULL,
  hometown VARCHAR(255) NOT NULL,
  mobile_phone VARCHAR(255) NOT NULL,
  college_id INT(2) ZEROFILL,
  PRIMARY KEY (id),
  Foreign KEY (college_id) REFERENCES colleges(id)
);

CREATE TABLE IF NOT EXISTS teachers (
  id INT(4) ZEROFILL NOT NULL UNIQUE AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  sex VARCHAR(255) NOT NULL,
  birthday VARCHAR(255) NOT NULL,
  title VARCHAR(255) NOT NULL,
  base_wage FLOAT,
  college_id INT(2) ZEROFILL,
  PRIMARY KEY (id),
  FOREIGN KEY (college_id) REFERENCES colleges(id)
);

CREATE TABLE IF NOT EXISTS courses (
  id INT(8) ZEROFILL NOT NULL UNIQUE AUTO_INCREMENT,
  name VARCHAR(50) NOT NULL,
  credit INT NOT NULL,
  credit_hour INT NOT NULL,
  college_id INT(2) ZEROFILL,
  PRIMARY KEY (id),
  Foreign Key (college_id) REFERENCES colleges(id)
);

CREATE TABLE IF NOT EXISTS class_schedule (
  id INT(8) ZEROFILL NOT NULL UNIQUE AUTO_INCREMENT,
  semester VARCHAR(255) NOT NULL,
  course_id INT(8) ZEROFILL,
  teacher_id INT(4) ZEROFILL,
  class_time VARCHAR(255) NOT NULL,
  PRIMARY KEY (id),
  Foreign Key (course_id) REFERENCES courses(id),
  Foreign Key (teacher_id) REFERENCES teachers(id)
);

CREATE TABLE IF NOT EXISTS course_selection (
  id INT(8) ZEROFILL NOT NULL UNIQUE AUTO_INCREMENT,
  student_id INT(4) ZEROFILL,
  class_schedule_id INT(8) ZEROFILL,
  semester VARCHAR(255) NOT NULL,
  course_id INT(8) ZEROFILL,
  teacher_id INT(4) ZEROFILL,
  performance_score INT,
  exam_score INT,
  final_score INT,
  PRIMARY KEY (id),
  Foreign Key (class_schedule_id) REFERENCES class_schedule(id),
  Foreign Key (student_id) REFERENCES students(id),
  Foreign Key (course_id) REFERENCES courses(id),
  Foreign Key (teacher_id) REFERENCES teachers(id)
);