#[test]
fn test_declare() {
    match declare('minimal') {
        Result::Ok(class_hash) => {
            assert(class_hash != 0, 'class_hash != 0');
        },
        Result::Err(x) => {
            let mut data = array_new::<felt>();
            array_append::<felt>(ref data, x);
            panic(data)
        },
    }
}

#[test]
fn test_declare_nonexistent() {
    match declare('abcdef') {
        Result::Ok(x) => {
            let mut data = array_new::<felt>();
            array_append::<felt>(ref data, x);
            panic(data)
        },
        Result::Err(x) => {
            let mut data = array_new::<felt>();
            array_append::<felt>(ref data, x);
            panic(data)
        },
    }
}

#[test]
fn test_declare_broken() {
    match declare('broken') {
        Result::Ok(x) => {
            let mut data = array_new::<felt>();
            array_append::<felt>(ref data, x);
            panic(data)
        },
        Result::Err(x) => {
            let mut data = array_new::<felt>();
            array_append::<felt>(ref data, x);
            panic(data)
        },
    }
}

#[test]
fn test_declare_cairo0() {
    match declare('cairo0') {
        Result::Ok(x) => {
            let mut data = array_new::<felt>();
            array_append::<felt>(ref data, x);
            panic(data)
        },
        Result::Err(x) => {
            let mut data = array_new::<felt>();
            array_append::<felt>(ref data, x);
            panic(data)
        },
    }
}
