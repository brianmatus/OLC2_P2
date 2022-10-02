fn change_first(x:i64, arr : &mut [[f64]]) {

    println!("arr:{:?}",arr);


    if x > 400 {
        println!("x>400");
    }
    println!("x<=400");


}


fn main() {

    let mut z = 22;

    //let mut xd : [[f64;3];1] = [[1.1,2.2,3.3]];

    let p = 10;

    //println!("xd:{:?}",arr);
    //change_first(420, &mut xd);
    change_first(420, &mut [[1.1,2.2,3.3]]);

}

//TODO add random args before arr to check for correct P reverse by ref