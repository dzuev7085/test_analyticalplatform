#!/bin/sh

psql -h postgres -U runner -d postgres -c "CREATE DATABASE django;"
psql -h postgres -U runner -d postgres -c "CREATE DATABASE dwh;"
psql -h postgres -U runner -d postgres -c "CREATE DATABASE dwh_tmp;"

##########
# Datalake
##########
psql -h postgres -U runner -d postgres -c "CREATE DATABASE datalake;"

# GLEIF
psql -h postgres -U runner -d datalake -c "CREATE SCHEMA gleif;"

# Findata
psql -h postgres -U runner -d datalake -c "CREATE SCHEMA findata;"
psql -h postgres -U runner -d datalake -c "CREATE TABLE findata.financial_statement(id BIGSERIAL, CONSTRAINT financial_statement_pkey PRIMARY KEY (id));"

# Static data
psql -h postgres -U runner -d datalake -c "CREATE SCHEMA static;"
psql -h postgres -U runner -d datalake -c "CREATE TABLE static.countryregion (id BIGSERIAL);"
psql -h postgres -U runner -d datalake -c "CREATE TABLE static.currency (id BIGSERIAL);"
psql -h postgres -U runner -d datalake -c "CREATE TABLE static.gicsindustry (id BIGSERIAL);"
psql -h postgres -U runner -d datalake -c "CREATE TABLE static.gicsindustrygroup (id BIGSERIAL);"
psql -h postgres -U runner -d datalake -c "CREATE TABLE static.gicssector (id BIGSERIAL);"
psql -h postgres -U runner -d datalake -c "CREATE TABLE static.gicssubindustry (id BIGSERIAL);"

# Company
psql -h postgres -U runner -d datalake -c "CREATE SCHEMA company;"
psql -h postgres -U runner -d datalake -c "CREATE TABLE company.entity (id BIGSERIAL);"

# Market data
psql -h postgres -U runner -d datalake -c "CREATE SCHEMA market_data;"
psql -h postgres -U runner -d datalake -c "CREATE TABLE market_data.fx (id BIGSERIAL);"
