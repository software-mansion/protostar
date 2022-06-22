# This scripts performs custom static checks in CI

# Check if all cairo test use @external decorator
find . -type f -name '*.cairo' | grep -z '@view.*\nfunc test_.*'
if [ $? -eq 0 ]; then
    exit 1
fi

exit 0