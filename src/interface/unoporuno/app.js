var express = require('express');
var http = require('http');
var path = require('path');
var favicon = require('static-favicon');
var logger = require('morgan');
var cookieParser = require('cookie-parser');
var bodyParser = require('body-parser');

var routes = require('./routes');
var users = require('./routes/user');

var app = express();
var engine = require('ejs-locals');
 
var validator = require('validator');

var eValidator = require('express-validator');

var mysql = require('mysql');

//Pour crypter les mots de passes
var crypto = require('crypto');

//Base de données et les différentes connections
var connection = mysql.createConnection({
  host     : 'localhost',
  user     : 'unoporuno',
  password : 'unoporuno',
  database : 'unoporuno'
});



//Le port dans lequel on va écouter
app.set('port', process.env.PORT || 3000);

//test
app.engine('ejs',engine);
app.use(express.static(__dirname+'/views'));
// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');

app.use(favicon());
app.use(logger('dev'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded());
//Utilisation d'express-Validator
app.use(eValidator());
app.use(cookieParser());

//Pour les sessions du site internet
app.use(express.session({
    //Clef privée
    "secret": "sOme2privAte3StrinG",
    // Internal session data storage engine, this is the default engine embedded with connect.
    // Much more can be found as external modules (Redis, Mongo, Mysql, file...). look at "npm search connect session store"
    "store":  new express.session.MemoryStore({ reapInterval: 60000 * 10 })
  }));


app.use(require('stylus').middleware(path.join(__dirname, 'public')));
app.use(express.static(path.join(__dirname, 'public')));
app.use(app.router);


// Les différentes routes pour nos vues.
app.get('/', routes.index);

app.get('/users', users.list);

app.get('/login', routes.login);

app.get('/register', routes.register);

app.get('/search', routes.search);

app.get('/search/:id', routes.persons);

app.get('/details', routes.details);

/** Les différentes fonctions **/

//Cette fonction retourne un tableau d'erreurs bien formaté
function getErrors(err)
{
    //Var de boucle
    var i = 0;
    //Notre tableau d'érreurs
    var errors = new Array();
    //Notre boucle qui repartit les différentes érreurs
    for(i = 0; i < err.length; i++)
    {
        //On implémente les érreurs
        errors[err[i].param] = err[i].msg;
    }

    return errors;
}

/** On effectue ici les différentes actions en post **/

//L'inscription
app.post('/register', function(req, res){

    //On crée une variable user
    var user = req.body;
    //Les érreurs
    var err = "Veuillez remplir tout les champs ci-dessous s'il vous plaît."
    //Les différentes variables qui correspondent
    var firstname = "", lastname = "", username = "", email = "", password = "";
    //On récupère les données postées
    firstname = user.firstname;
    lastname = user.lastname;
    username = user.username;
    email = user.email;
    password = user.password;

    //On va valider nos paramètres & on y met les différentes érreurs
    req.checkBody('firstname','Un prénom est requis pour l\'enregistrement.').notEmpty();
    req.checkBody('lastname','Un nom est requis pour l\'enregistrement.').notEmpty();
    req.checkBody('username','Un pseudo est requis pour l\'enregistrement.').notEmpty();
    req.checkBody('email','Un email valide est requis.').isEmail();
    req.checkBody('password','Le champs mot de passe ne peut rester vide.').notEmpty();

    //Les différentes érreurs
    var errors = req.validationErrors();
    //Si un de nos éléments est vide.
    if(errors)
    {
        console.log(errors);
        //Données à la vue
        var data = {title: 'N\'hesitez pas à vous inscrire pour pouvoir accéder à toute l\'application.', 
                    description: 'Inscrivez vous en moins de 60 secondes.', 
                    layoutFile: 'layout',
                    err:err,
                    username: "",
                    id: "",
                    errors: getErrors(errors),
                };

        //On envoie à la vue register
        res.render('register',data);
    }

    //Vérifions si l'email ou le pseudo n'existe déjà pas dans notre base de données
    var verif = "SELECT COUNT(*) as userExist from auth_user where email = ? OR username = ?";

    connection.query(verif,[email,username],function(err, rows){

        //Si il y a une érreur
        if(err != null)
        {
            res.end("Erreur requête: "+err);
        }
        else
        {

            //Si le résultat est supèrieur à 0
            if(rows[0].userExist > 0)
            {
                    //Erreur
                    var err = "Pseudo ou Email déjà utilisé!!!";
                    //Données à la vue
                    var data = {
                        title: 'N\'hesitez pas à vous inscrire pour pouvoir accéder à toute l\'application.', 
                        description: 'Inscrivez vous en moins de 60 secondes.', 
                        layoutFile: 'layout',
                        username: "",
                        id: "",
                        err:err,
                        errors: new Array()
                    };

                    //On renvoie vers la page d'inscription avec l'érreur
                    res.render('register',data);
            }
            else
            {
                //On hashe le mot de passe avec la clef hash1
                password = crypto.createHash('sha1').update(password).digest('hex');

                //Requête d'insertion dans la base de données
                var insert = "INSERT INTO auth_user(username,first_name,last_name,email,password) VALUES(?,?,?,?,?)";

                connection.query(insert,[username,firstname,lastname,email,password],function(err){
                    //Si erreur lors de l'enregistrement.
                    if(err != null)
                    {
                        res.end("Erreur requête: "+err);
                    }
                    else
                    {
                        console.log("Utilisateur enregistré.");
                        //On renvoie vers la page d'inscription avec l'érreur
                        res.redirect('/login');
                    }
                });
                        
            }
        }
    });

});

//Connexion
app.post('/login', function(req,res){

    //On crée une variable user
    var user = req.body.user;
    //Nos variable pour le login
    var email = user.email, password = user.password;

    //On hashe le mot de passe avec la clef hash1
    password = crypto.createHash('sha1').update(password).digest('hex');

    //Notre requete
    var verif= "SELECT * from auth_user where email = ? && password = ?";

    //On fait la vérification avec les paramètres
    connection.query(verif,[email,password],function(err,rows){
        //Si il y a une érreur on l'affiche
        if(err != null)
        {
            res.end("Erreur requête: "+err);
        }
        else
        {
            console.log(rows);
            //On verifit si on a pu récupérer une ligne
            if(rows.length > 0)
            {
                console.log("Utilisateur connecté!!!");

                //On crée des variables sessions correspondant au client
                req.session.username = rows[0].username;
                req.session.id = rows[0].id;

                res.redirect('/');
            }
            else
            {
                err = "Le couple Login/Mot de passe ne correspond pas."
                console.log("Mauvais identifiants!!!");
                //Quelques données
                var data = {title: 'Connectez vous afin de pouvoir accéder au site entier.', 
                            description: 'Pas encore connecté, allez y et vous pourrez avoir acccès à tout.', 
                            layoutFile: 'layout',
                            username: "",
                            id: "",
                            err:err};

                res.render('login',data);
            }

        }
    });


});

// catch 404 and forwarding to error handler
app.use(function(req, res, next) {
    var err = new Error('Not Found');
    err.status = 404;
    next(err);
});

// error handlers

// development error handler
// will print stacktrace
if (app.get('env') === 'development') {
    app.use(function(err, req, res, next) {
        res.render('error', {
            message: err.message,
			title: err.message,
            error: err
        });
    });
}

// production error handler
// no stacktraces leaked to user
app.use(function(err, req, res, next) {
    res.render('error', {
        message: err.message,
        error: {}
    });
});


module.exports = app;

http.createServer(app).listen(app.get('port'), function(){
	console.log('Express écoute sur le port '+ app.get('port'));
});