//Objet mysql
var bdd = require('mysql');
//Nouvelle connection à la base de données
var bddConnection = bdd.createConnection({
  host     : 'localhost',
  user     : 'unoporuno',
  password : 'unoporuno',
  database : 'unoporuno'
});

/** Nos différentes fonctions de callBack **/

//Renvoie l'érreur
function getError(err)
{
  console.log("Fail: "+err);
}

//Fonction qui vérifit si le client est connecté
function isConnected (req, res) 
{
  //Si le client est connecté
  if(req.session.username)
  {
    //On lui donne accès
    console.log("Utilisateur connecté sur la page.")
  } 
  else 
  {
    //Sinon on le redirige vers la page de login
    res.redirect("/login");
  }
}
//Teste si l'utilisateur est déjà connecté
function isAlwaysConnected(req,res)
{
  //Si le client est connecté
  if(req.session.username)
  {
    //Une redirection vers la page d'accueil
    res.redirect('/');
  }

}

/* GET home page. */
exports.index = function(req, res){

  //On vérifit si le client est connecté
  isConnected(req,res);
  //On récupère la liste des recherches ordonnées par id desc
  var recup = "SELECT * from  unoporuno_busqueda order by id desc";
  //On applique la requête avec la fonction getData qui récupère les données
  bddConnection.query(recup,function(err,rows){

    //Si il y a une érreur on l'affiche
    if(err)
    {
      return getError(err);
    }
    else
    {
      //Différentes données à passer en url à la page
      var data = {title: 'Bienvenue sur le projet révolutionnaire Unoporuno', 
                  description: 'Liste des récentes recherches.', 
                  layoutFile: 'layout',
                  username: req.session.username,
                  id: req.session.id,
                  data: rows};
      //On envoie les données à la vue
      res.render('index',data);
    }
  });
  
};

/* GET login page. */
exports.login = function(req, res){

  //S'il est déjà connecté on le redirige vers la page d'accueil
  isAlwaysConnected(req,res);
  //Quelques données
  var data = {title: 'Connectez vous afin de pouvoir accéder au site entier.', 
              description: 'Pas encore connecté, allez y et vous pourrez avoir acccès à tout.', 
              layoutFile: 'layout',
              username: "",
              id: "",
              err:""};
  
  res.render('login',data);
};

/* GET register page. */
exports.register = function(req, res){

  //S'il est déjà connecté on le redirige vers la page d'accueil
  isAlwaysConnected(req,res);
  //Erreur générale
  var err = "";
  //Les erreurs
  var errors = new Array();

  //Quelques données
  var data = {title: 'N\'hesitez pas à vous inscrire pour pouvoir accéder à toute l\'application.', 
              description: 'Inscrivez vous en moins de 60 secondes.', 
              layoutFile: 'layout',
              username: "",
              id: "",
              errors: errors,
              err:err};

  res.render('register',data);
};

/* GET search page. */
exports.search = function(req, res){

  //On vérifit si le client est connecté
  isConnected(req,res);
  //Quelques données
  var data = {title: 'Faites votre recherche ici.', 
              description: 'Rechercher un expert.', 
              layoutFile: 'layout',
              username: req.session.username,
              id: req.session.id,
            };

  res.render('search',data);
};

/* GET search by id. */
exports.persons = function(req, res){
  //On vérifit si le client est connecté
  isConnected(req,res);
  //Récupérons l'id
  var id = parseInt(req.params.id);
  //On prépare notre requête
  var recup = "SELECT * from unoporuno_persona where busqueda_id = ?";
  //On applique la requête avec la fonction getData qui récupère les données
  bddConnection.query(recup,[id],function(err,rows){
      //Si il y a une érreur on l'affiche
    if(err)
    {
      return getError(err);
    }
    else
    {
      //Différentes données à passer en url à la page
      var data = {title: 'Recherche n° '+id, 
                  description: 'Liste des récentes recherches.', 
                  layoutFile: 'layout',
                  username: req.session.username,
                  id: req.session.id,
                  data: rows};

      //On envoie la réponse à une page html
      res.render('persons',data);
    }
  });

};


/* GET details page. */
exports.details = function(req, res){

  //On vérifit si le client est connecté
  isConnected(req,res);
  //Quelques données
  var data = {title: 'Détails de la personne X.', 
              description: 'Différents résultats sur X.', 
              layoutFile: 'layout',
              username: req.session.username,
              id: req.session.id,
            };

  res.render('details',data);
};