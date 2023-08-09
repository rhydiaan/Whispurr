use std::io;
use num_derive::FromPrimitive;
use num_traits::FromPrimitive;

#[derive(FromPrimitive)]
enum Inputs{
    Invalid = 0,
    Login = 1,
    SignUp = 2,
}


fn main() {

    println!("Welcome to Whispurr! Please choose to either login or create a user.");
    
    user_choice();

}


fn user_choice() {

    println!("To login please type \'1\' or to create a user please type \'2\' \n");

    let mut choice = String::new();

    io::stdin().read_line(&mut choice).expect("failed to readline");

    let trimmed_choice = choice.trim();

    if trimmed_choice.is_empty() {
        println!("\nInvalid input: Empty choice");
        return;
    }

    match FromPrimitive::from_u8(trimmed_choice.parse::<u8>().unwrap_or(0)) {
        Some(Inputs::Login) => {
            login(trimmed_choice);
        }
        Some(Inputs::SignUp) => {
            sign_up(trimmed_choice);
        }
        _ => {
            println!("Invalid choice");
            user_choice();
        }
    }
}

fn login(choice: &str) {
    println!("\nYou chose Login with the choice {}", choice);
}

fn sign_up(choice: &str) {
    println!("\nYou chose Sign Up with the choice {}", choice);
}

// {
// 	"CreateUser" : {
// 		"id" : "user_id",
// 		"password" : "password"
// 	}
// }

// {
// 	"Login" : {
// 		"id" : "user_id",
// 		"password" : "password"
// 	}
// }

// {
// 	"SendMessage" : {
// 		"message" : "Hello world!",
// 		"target" : "target_id"
// 	},
// 	"id" : "sender_id"
// }