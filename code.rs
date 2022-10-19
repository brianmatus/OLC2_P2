fn main() {
    //let mut vector = vec![vec![1,2,3,4,5]];
    //let mut vector : Vec<i64> = Vec::with_capacity(10);
    //let mut vector : Vec<i64> = Vec::new();
    let mut a : Vec<i64> = vec![1,2,3,4,5];

    let mut b = a.remove(2);
    print!("a:{:?}", a);
    print!(" len:{}", a.len());
    println!(" capacity:{}", a.capacity());

    println!("b:{}", b);




}

