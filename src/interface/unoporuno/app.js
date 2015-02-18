
/**
*
*
#/usr/bin/env nodeJS
## -*- coding: utf-8 -*-
##
## Copyright (c) 2014 Dominick Makome
**
**/

var express = require('express');
//Appel du module google
var google =  require('google');

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

// Le serveur socket
var net = require('net');
//Base de données et les différentes connections
var connection = mysql.createConnection({
  host     : 'localhost',
  user     : 'unoporuno',
  password : 'unoporuno',
  database : 'unoporuno'
});

//Le port dans lequel on va écouter
app.set('port', process.env.PORT || 3000);
//On envoie le host
app.set('host','127.0.0.1');

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

app.get('/google', routes.google);

app.get('/search/:id', routes.persons);

app.get('/details/:id', routes.details);

app.get('/logout',routes.logout);
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



/**
*
* Cette fonction crée des requêtes aléatoirement, ensuite fait appel à la fonction
* Google pour effectuer avec un délai de 60 secondes entre chaque requêtes.
*
*/
function query_bdd(req,res) 
{

    //On récupère nos deux paramètres cruciaux
    var busqueda_id = req.session.busqueda_id;
    var persona_id = req.session.persona_id;

    //Applique la requête
    //On récupère la liste des requêtes
    var recup = "SELECT * from unoporuno_requete WHERE persona_id = ? && busqueda_id = ?"; 
    //REQUETE d extraction des infos de la table unoporuno_requete
    connection.query(recup,[persona_id,busqueda_id],function(err, rows) {
            //Si erreur
            if (err) throw err;
            else
            {
            
              for(var i = 0; i < rows.length; i++)
              {

                console.log(rows[i].id+" : "+rows[i].content+" "+rows[i].type_r);
                //attente de 60 seconde entre chaque requete google @Anthony faisait ou presque
                setTimeout(google_req(rows[i].content,req,res),60000);

              }
              
            }
        
    });

}


/**
  * Requete google qui prend en parametre un attribut de la base de données unoporuno_requete avec une recherche efféctuée 
  */
function google_req(content,req,res)
{
        //Maximum de 10 résultats par requete.
        google.resultsPerPage = 10;

        google(content,function(err,next,links){

            //On est bel et bien dans le script google
            console.log("In google script");

            //affiche le rapport d'erreur dans la console
            if (err) console.error(err);
            //Si vaut null, alors aucun résultat par google
            if(next == null)
            {
              res.write("Aucun résultat n'a été trouvé!");
              res.end();
            }     

            //pour chaque resultat on affiche le titre de la page et sa description comme sur google
            for(var i = 0; i<links.length;i++)
            {
                persona_id = req.session.persona_id;
                title =  links[i].title;
                description =  links[i].description;
                link = links[i].link;

                console.log("Insertion n° "+i);
                //Insertion des données dans la base de données unoporuno_snippet
                insert = "INSERT INTO unoporuno_snippet (persona_id,query,title,description,link) VALUES(?,?,?,?,?)";

                connection.query(insert,[persona_id,content,title,description,link]);
            }
        
      });

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


//Si une recherche a été déclenchée
app.post('/search',function(req, res){

    //On crée une variable recherche
    var search = req.body.search;
    //Variable qui va gérer les érreurs
    var error = "";

    //Nos différents champs de recherches
    var name = search.name;
    var description = search.description;
    var geo = search.geo;
    var status = "En cours de traitement";

    //Nom de l'utilisateur qui effectue sa recherche
    var username = req.session.username;

    console.log(search);


    //Si tout les champs sont vides alors une érreur sera déclenchée
    if(name == '' || description == '' || geo == '')
    {
        console.log("La description et le nom sont des champs obligatoires.");
        //On crée notre érreur
        err = "Tout les champs ci dessous sont obligatoires.";

        //Quelques données
        var data = {title: 'Faites votre recherche ici.', 
                    description: 'Rechercher un expert.', 
                    layoutFile: 'layout',
                    username: req.session.username,
                    id: req.session.id,
                    err:err,
            };

        res.render('search',data);
    }
    else
    {
        //Cela veut dire que les champs obligatoires sont remplis
        var insert = "INSERT INTO unoporuno_busqueda (nombre,fecha,usuario,descripcion,status) VALUES(?,?,?,?,?)";
        var now  = new Date();

        //On insert nos données dans la bonne table d'utilisation
        connection.query(insert,[name,now,username,description,status],function(err){

            if(err) throw err;
            else
            {
                //On récupère le busqueda_id pour faire une bonne insertion
                recup = "SELECT id from unoporuno_busqueda WHERE nombre = ? && usuario = ? && descripcion = ? ORDER BY id DESC LIMIT 1";

                //On applique la requête de récupération
                connection.query(recup,[name,username,description],function(err,rows){

                    if(err) throw err;
                    else
                    {
                        //On enregistre l'id du busqueda(de la recherche)
                        var busqueda_id = rows[0].id;
                        //On fait une seconde insertion dans la table unoporuno_persona
                        insert = "INSERT INTO unoporuno_persona (busqueda_id,name,geo,orgs,topics) VALUES(?,?,?,?,?)";
                        //On applique l'enregistrement  des données une fois de plus
                        connection.query(insert,[busqueda_id,name,geo,description,description],function(err){

                            if(err) throw err;
                            else
                            {
                                //On fait une insertion dans la table unoporuno_requete

                                //On récupère persona_id
                                recup = "SELECT id from unoporuno_persona WHERE busqueda_id = ? && name = ? && geo = ? && orgs = ?  && topics = ? ORDER BY id LIMIT 1";

                                //On applique la requête
                                connection.query(recup,[busqueda_id,name,geo,description,description],function(err,rows){

                                    if(err) throw err;
                                    else
                                    {
                                        //On enregistre persona_id
                                        persona_id = rows[0].id;
                                        //On fait une redirection vers la page google qui va faire les requêtes préparées chez google
                                        req.session.persona_id = parseInt(persona_id);
                                        req.session.busqueda_id  = parseInt(busqueda_id);

                                        console.log("Avant Fouille.");

                                        /* Faire appel à la fouille de données */
                                        //Création du serveur
                                        net.createServer(function(socket){

                                                socket.on('error',function(err){
                                                    console.log("Erreur : ");
                                                    console.log(err.stack);

                                                    res.redirect('/');
                                                });


                                                //On ouvre la socket et on lit les données
                                                socket.on('data', function(data){
                                                        //Données envoyées par Python
                                                        console.log('DATA BY PYTHON' + socket.remoteAddress + ': ' + data);

                                                        //1er Envoie
                                                        if(data == "Begin")
                                                        {
                                                            //On envoie
                                                            send = "un";
                                                            //On envoie le premier send
                                                            socket.write(send);
                                                            //On constitue les données qui seront envoyés 
                                                            send = req.session.busqueda_id+'#'+req.session.persona_id+'#'+name+'#'+description+'#'+geo;
                                                            //On envoie les données
                                                            socket.write(send);
                                                        }
                                                        else if(data == "true")
                                                        {
                                                            query_bdd(req,res);
                                                            //On envoie
                                                            send = "deux";
                                                            //On envoie le send
                                                            socket.write(send);
                                                        }
                                                        else if(data == "second")
                                                        {
                                                            //Ferméture de la socket
                                                            socket.on('close',function(data){
                                                                console.log('Socket Fermée.');
                                                            });

                                                            //On redirige vers l'accueil
                                                            res.redirect('/');
                                                        }
                                                        else
                                                        {
                                                            console.log('Nothing!!!!!');
                                                        }

                                                });

                                        }).listen(3200,app.get('host'));
                                        /* Fouille fini */

                                        //On redirige vers la page google
                                        //res.redirect('/google');
                                    }

                                });
                            }

                        });

                    }
                });

            }

        });
    }

});

//Si on affine la recherche sur la langue
app.post('/details/:id',function(req,res){

    //On récupère tout les paramètres qui sont passé
    var params = req.body;

    //On récupère les langues et l'id de la personne
    var lang = params.lang;
    var persona_id = parseInt(params.persona_id);
    //On va récupérer tout les snippets des langues spécifiées
    var i = 0;
    //Notre requête de récupération des filtres
    var recup = "SELECT DISTINCT * from (unoporuno_snippet JOIN unoporuno_features) WHERE (unoporuno_features.value = ? && unoporuno_snippet.persona_id = ? && unoporuno_snippet.id = unoporuno_features.snippet_id)";
    var _data  = {};
    //On récupère la première langue ou la première lettre
    var langue  = lang[0];

    //Si la personne a choisi plusieurs langues
    if(langue.length > 1)
    {
        //On parcourt les langues puis on applique une requête
        for(i = 0; i < lang.length; i++)
        {
            //On récupère la langue courante
            langue = lang[i];
            //On applique la requête de récupération
            connection.query(recup,[langue,persona_id],function(err,rows){

                if(err) throw err;
                else
                {
                    //On met les données dans une variable
                    _data[i] = rows;
                }
            });
        }
    }
    //Si elle a choisit qu'une seule langue
    else
    {
        //On récupère le nom de la personne
        var recup_name = "SELECT * from unoporuno_persona where id = ?";
        var nameOf = "";
        //On applique la requête pour récupérer le nom
        connection.query(recup_name,[persona_id],function(err,rows){

              if(err) throw err;
              else
              {
                    //Nom de l'utilisateur
                    nameOf = rows[0].name;
                    //On applique la requête sur la langue si ce n'est qu'une langue
                    connection.query(recup,[lang,persona_id],function(err,rows){
                        if(err) throw err;
                        else
                        {
                            console.log(rows);
                            //Récupération de toutes les langues
                            recup2 = "SELECT DISTINCT value from unoporuno_features";
                            //Connection pour récupérer les valeurs
                            connection.query(recup2,function(error,rows2){

                                if(error) return getError(error);
                                else
                                {
                                    //Différentes données à passer en url à la page
                                    var data = {title: 'Résultat(s) sur la recherche: "'+nameOf+'"', 
                                                description: 'Différents résultats sur la recherche "'+nameOf+'"',
                                                persona_id:persona_id, 
                                                layoutFile: 'layout',
                                                username: req.session.username,
                                                id: req.session.id,
                                                selected:lang,
                                                data: rows,
                                                lang: rows2};
                                    //On envoie la réponse à une page html
                                    res.render('details',data);
                                }

                            });
                        }
                    });

              }
        });
        
    }

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