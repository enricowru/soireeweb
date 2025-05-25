const mongoose = require("mongoose");

mongoose.connect("mongodb+srv://enricowru:test1234@cluster0.yahkvow.mongodb.net/createUser?retryWrites=true&w=majority&appName=Cluster0", {
  useNewUrlParser: true,
  useUnifiedTopology: true
})
.then(() => {
  console.log("✅ Mongoose connected to MongoDB Atlas");
})
.catch((e) => {
  console.error("❌ Connection failed:", e);
});

const userSchema = new mongoose.Schema({
  firstname: { type: String, required: true },
  lastname: { type: String, required: true },
  username: { type: String, required: true, unique: true },
  mobile: { type: String, required: true },
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true }
});

const LogInCollection = mongoose.model("LogInCollection", userSchema);
module.exports = LogInCollection;
