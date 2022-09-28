//fn ola(x : i64) {
//    let mut offset1 = 33;
//    let mut offset2 = 44;
//
//    println!("recibido:{}",x);
//
//}


fn main () {
    //let x = 11;
    //ola(420);
    //let y = 22;
    //ola(421);

    //println!("Prueba de datos corrompidos");
    //println!("x:{}",x);
    //println!("y:{}",y);

    let mut arr1 = [[1,2],[3,4]];
    let mut arr2 = arr1;

    arr2[0][0] = 42;

    println!("Prueba de referencia de arrays");
    println!("arr1:{:?}",arr1);
    println!("arr2:{:?}",arr2);


}


