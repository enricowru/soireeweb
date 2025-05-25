const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
const bodyParser = require("body-parser");

const app = express();

// MIDDLEWARES
app.use(cors());
app.use(express.json());
app.use(bodyParser.urlencoded({ extended: false }));

// CONNECT TO MONGODB ATLAS
mongoose.connect("mongodb+srv://enricowru:test1234@cluster0.yahkvow.mongodb.net/createUser?retryWrites=true&w=majority&appName=Cluster0", {
  useNewUrlParser: true,
  useUnifiedTopology: true,
})
.then(() => console.log("✅ Connected to MongoDB Atlas"))
.catch((err) => console.error("❌ Connection error:", err));

// DEFINE USER SCHEMA WITH VALIDATION
const LogInSchema = new mongoose.Schema({
  firstname: { type: String, required: true },
  lastname: { type: String, required: true },
  username: { type: String, required: true, unique: true },
  mobile: { type: String, required: true },
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true }
});

// CREATE MONGOOSE MODEL
const LogInCollection = mongoose.model("LogInCollection", LogInSchema);

// SIGNUP ROUTE
app.post("/signup", async (req, res) => {
  const { firstname, lastname, username, mobile, email, password } = req.body;

  try {
    const existingUser = await LogInCollection.findOne({ username });
    if (existingUser) {
      return res.status(400).json({ message: "Username already exists." });
    }

    const newUser = new LogInCollection({
      firstname,
      lastname,
      username,
      mobile,
      email,
      password
    });

    await newUser.save();
    return res.status(201).json({ message: "User registered successfully." });
  } catch (err) {
    return res.status(500).json({ message: "Server error", error: err.message });
  }
});

// LOGIN ROUTE
app.post("/login", async (req, res) => {
  const { username, password } = req.body;

  try {
    const user = await LogInCollection.findOne({ username });

    if (!user) {
      return res.status(404).json({ message: "User not found." });
    }

    if (user.password !== password) {
      return res.status(401).json({ message: "Incorrect password." });
    }

    return res.status(200).json({
      message: "Login successful",
      user: {
        firstname: user.firstname,
        lastname: user.lastname,
        username: user.username,
        email: user.email,
        mobile: user.mobile
      }
    });
  } catch (err) {
    return res.status(500).json({ message: "Server error", error: err.message });
  }
});

// START SERVER
const PORT = 3000;
app.listen(PORT, () => {
  console.log(`🚀 Server running at https://soireeweb.onrender.com`);
});
