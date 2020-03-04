CREATE TABLE Alunni          (
			CodicePersona   










			char(6) PRIMARY KEY,

Nome varchar(35),

	Cognome

varchar(35)


				);

		CREATE
	TABLE
				Esame
	(    CodEsame char(6) PRIMARY KEY,

		Studente char(6) REFERENCES Alunno(Matricola) ON UPDATE CASCADE ON DELETE NO ACTION,
		

		Voto integer











	);


