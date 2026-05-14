CREATE TABLE network_providers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(10) NOT NULL
);

CREATE TABLE members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fname VARCHAR(30) NOT NULL,
    lname VARCHAR(30) NOT NULL,
    date_of_birth DATE NOT NULL,
    phone_number VARCHAR(15) NOT NULL,
    age INT NOT NULL,
    email VARCHAR(50) NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE plans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    provider_id INT NOT NULL,
    name VARCHAR(20) NOT NULL,
    data_gb DECIMAL(5,1),
    unlimited_data BOOLEAN DEFAULT FALSE,
    calls VARCHAR(10),
    texts VARCHAR(10),
    phone_included VARCHAR(30),
    monthly_price DECIMAL(6,2) NOT NULL,
    FOREIGN KEY (provider_id) REFERENCES network_providers(id)
);

CREATE TABLE memberships (
    id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,
    plan_id INT NOT NULL,
    monthly_price DECIMAL(6,2) NOT NULL,
    spending_cap_active BOOLEAN DEFAULT FALSE,
    spending_cap_amount DECIMAL(6,2) DEFAULT NULL,
    age_restricted BOOLEAN DEFAULT FALSE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    FOREIGN KEY (member_id) REFERENCES members(id),
    FOREIGN KEY (plan_id) REFERENCES plans(id)
);