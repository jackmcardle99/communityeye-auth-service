-- 
-- File: V1.1__Remove_is_deleted_column.sql
-- Author: Jack McArdle

-- This file is part of CommunityEye.

-- Email: mcardle-j9@ulster.ac.uk
-- B-No: B00733578
-- 

ALTER TABLE users DROP COLUMN is_deleted;