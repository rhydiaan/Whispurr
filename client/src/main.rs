use std::io;
use num_derive::FromPrimitive;
use num_traits::FromPrimitive;
use url::Url;
use tungstenite::{connect, Message};

// Enum to represent user inputs
#[derive(FromPrimitive)]
enum Inputs{
    Invalid = 0,
    Login = 1,
    CreateUser = 2,
}

// Struct to store user credentials
struct User {
    username: String,
    password: String,
}

// Function to handle user's choice
fn user_choice() {

    println!("To login please type \'1\' or to create a user please type \'2\' \n");

    let mut choice = String::new();

    io::stdin().read_line(&mut choice).expect("failed to readline");

    let trimmed_choice = choice.trim();

    if trimmed_choice.is_empty() {
        println!("\nInvalid input: Empty choice");
        return;
    }

    // Match user's choice
    match FromPrimitive::from_u8(trimmed_choice.parse::<u8>().unwrap_or(0)) {
        Some(Inputs::Login) => {
            login(trimmed_choice);
        }
        Some(Inputs::CreateUser) => {
            create_user(trimmed_choice);
        }
        _ => {
            println!("Invalid choice");
            user_choice(); // Allow the user to re-enter a valid choice
        }
    }
}

// Function to get user's credentials
fn get_user_credentials(choice: u8) -> User {
    
    // Match if user is logging in or creating a user
    match FromPrimitive::from_u8(choice) { 
        Some(Inputs::Login) => {
            println!("To login please type your username:");
        }
        Some(Inputs::CreateUser) => {
            println!("To create a user please type your username:");
        }
        _ => {
            println!("Invalid choice");
        }
    }

    let mut username = String::new(); // Getting username

    io::stdin().read_line(&mut username).expect("failed to readline"); // Getting user input

    let trimmed_username = username.trim();

    if trimmed_username.is_empty() {
        println!("\nInvalid input: Empty username");
        user_choice(); // Allow the user to re-enter a valid username
    }

    println!("And now password:"); // Getting user password

    let mut password = String::new(); // Defining password to empty String

    io::stdin().read_line(&mut password).expect("failed to readline"); // Getting user input

    let trimmed_password = password.trim();

    if trimmed_password.is_empty() {
        println!("\nInvalid input: Empty password");
        user_choice(); // Allow the user to re-enter a valid password
    }

    User { // Creating struct from user inputs and returning the struct
        username: String::from(trimmed_username),
        password: String::from(trimmed_password),
    }

}

// Function to handle login
fn login(choice: &str) {

    let user = get_user_credentials(choice.parse::<u8>().expect("Error parsing choice")); // Getting user credentials 

    // Connecting to websocket server
    let (mut socket, _) = connect(
        Url::parse("wss://localhost:11000").unwrap()
    ).expect("Can't connect");

    println!("\nYou chose Login with the choice {}", choice);
    
    let message = format!(
        r#"{{
            "Login" : {{
                "id" : "{}",
                "password" : "{}"
            }}
        }}"#, user.username, user.password);
    

    let _ = socket.send(Message::Text(message)); // Sending login request to server

    loop { // Listening for anything coming through the websocket
        let msg = socket.read().expect("Error reading message");
        println!("Received: {}", msg);
    }
    
}

// Function to handle user creation
fn create_user(choice: &str) {

    let user = get_user_credentials(choice.parse::<u8>().expect("Error parsing choice")); // Getting user credentials 

    // Connecting to websocket server
    let (mut socket, _) = connect(
        Url::parse("wss://localhost:11000").unwrap()
    ).expect("Can't connect");

    println!("\nYou chose Sign Up with the choice {}", choice);
    
    let message = format!(
        r#"{{
            "CreateUser" : {{
                "id" : "{}",
                "password" : "{}"
            }}
        }}"#, user.username, user.password);
    
    let _ = socket.send(Message::Text(message)); // Sending user creation request to server

    loop { // Listening for anything coming through the websocket
        let msg = socket.read().expect("Error reading message");
        println!("Received: {}", msg);
    }
    
}

fn main() {

    println!("Welcome to Whispurr! Please choose to either login or create a user.");
    
    user_choice();

}

// TODO: 
//  - Handle message sending logic
//  - Tidy up recieving messages
// {
// 	"SendMessage" : {
// 		"message" : "Hello world!",
// 		"target" : "target_id"
// 	},
// 	"id" : "sender_id"
// }