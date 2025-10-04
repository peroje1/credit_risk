DROP TABLE IF EXISTS risk_results;
DROP TABLE IF EXISTS overdue;
DROP TABLE IF EXISTS income;
DROP TABLE IF EXISTS credit_bureau;
DROP TABLE IF EXISTS customer;

CREATE TABLE customer (
    date DATE NOT NULL,
    customer_id INT NOT NULL,
    birth_date DATE NOT NULL,
    sex CHAR(1) NOT NULL,        -- 'M' ili 'F'
    PRIMARY KEY (date, customer_id)
) ENGINE=InnoDB;

CREATE TABLE credit_bureau (
    date DATE NOT NULL,
    customer_id INT NOT NULL,
    installment_amount DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (date, customer_id),
    CONSTRAINT fk_cb_customer
      FOREIGN KEY (date, customer_id) REFERENCES customer(date, customer_id)
      ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE income (
    date DATE NOT NULL,
    customer_id INT NOT NULL,
    income_date DATE NOT NULL,
    income_type TINYINT NOT NULL,        -- 1=plata, 2=penzija, 3=ostalo
    income_amount DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (date, customer_id, income_date, income_type),
    CONSTRAINT fk_income_customer
      FOREIGN KEY (date, customer_id) REFERENCES customer(date, customer_id)
      ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE overdue (
    date DATE NOT NULL,
    customer_id INT NOT NULL,
    overdue_date DATE NOT NULL,
    PRIMARY KEY (date, customer_id),
    CONSTRAINT fk_overdue_customer
      FOREIGN KEY (date, customer_id) REFERENCES customer(date, customer_id)
      ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE risk_results (
    date DATE NOT NULL,
    customer_id INT NOT NULL,
    score DECIMAL(9,6) NOT NULL,
    probability DECIMAL(9,6) NOT NULL,
    PRIMARY KEY (date, customer_id)
) ENGINE=InnoDB;
