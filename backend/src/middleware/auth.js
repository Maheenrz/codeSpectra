const jwt = require('jsonwebtoken');

exports.authenticate = (req, res, next) => {
  try {
    // Get token from header
    const token = req.header('Authorization')?.replace('Bearer ', '');

    if (!token) {
      return res.status(401).json({ message: 'No token, authorization denied' });
    }

    // Verify token
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();

  } catch (error) {
    res.status(401).json({ message: 'Token is not valid' });
  }
};

exports.isInstructor = (req, res, next) => {
  if (req.user.role !== 'instructor' && req.user.role !== 'admin') {
    return res.status(403).json({ message: 'Access denied. Instructor only.' });
  }
  next();
};

exports.isStudent = (req, res, next) => {
  if (req.user.role !== 'student') {
    return res.status(403).json({ message: 'Access denied. Student only.' });
  }
  next();
};