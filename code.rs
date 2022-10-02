fn change_first(counter: i64) -> i64 {
    println!("ola k ase, retornando o k ase");
    return counter*2;
}


fn main() {
    let mut i = 0;
    println!("r:{}", change_first(i));
    i = i + 1;
    println!("r:{}", change_first(i));
}

//TODO add random args before arr to check for correct P reverse by ref