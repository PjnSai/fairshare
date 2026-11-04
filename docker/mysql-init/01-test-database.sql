-- Lets the app's database user create the temporary database Django uses for tests.
GRANT ALL PRIVILEGES ON `test\_fairshare`.* TO 'fairshare'@'%';