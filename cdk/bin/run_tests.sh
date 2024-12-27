# Run CDK tests
pytest test || exit "$?"
for dir in \
  lambdas/launcher \
  lambdas/servers
  do
  (
    cd "$dir"
    # Run lambda tests
    pytest test
  ) || exit "$?"
done
