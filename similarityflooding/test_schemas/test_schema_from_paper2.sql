CREATE TABLE Employee (
EmpNo int PRIMARY KEY,
EmpName varchar(50),
DeptNo int REFERENCES Department,
Salary dec(15.2),
Birthdate date
);

CREATE TABLE Department (
DeptNo int PRIMARY KEY,
DeptName varchar(70)
);