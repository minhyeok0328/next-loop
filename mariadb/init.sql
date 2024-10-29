CREATE DATABASE IF NOT EXISTS `next-loop`;

USE `next-loop`;

CREATE TABLE IF NOT EXISTS `hotel_order` (
    order_seq INT auto_increment NOT NULL,
    room_seq INT NOT NULL,
    customer_seq INT NOT NULL,
    order_price INT DEFAULT 0 NULL,
    status varchar(15) NOT NULL,
    contents LONGTEXT NULL,
    reg_date DATETIME NULL,
    check_date DATETIME NULL,
    refuse_date DATETIME NULL,
    complete_date DATETIME NULL,
    room_building_seq INT NULL,
    room_floor_seq INT NULL,
    room_name INT NULL,
    customer_name TEXT NULL,
    visitor_cnt INT NULL,
    visit_adult_cnt INT NULL,
    visit_child_cnt INT NULL,
    visit_baby_cnt INT NULL,
    check_in DATETIME NULL,
    check_out DATETIME NULL,
    check_out_expected DATETIME NULL,
    CONSTRAINT hotel_order_pk PRIMARY KEY (order_seq)
);
